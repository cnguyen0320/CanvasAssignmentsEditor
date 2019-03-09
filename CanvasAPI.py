#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 17:45:08 2019

@author: Chris Nguyen
contact: clnguyen2@wisc.edu
"""

import requests

class Canvas:
    def __init__(self, base_url, courseID, token):
        """
        Canvas object to get and change assignments
        """
        
        #add the backslash if it is missing
        if base_url[-1] != '/':
            base_url = base_url+'/'
        
        self.base_url = base_url+'api/v1/'
        self.headers = {'Authorization Bearer':token}
        self.courseID = courseID
    
    def __repr__(self):
        return "Canvas Course: " + str(self.courseID)
    
    def toJson(response):
        if not response.ok:
            print('Error in response', response.status_code, response.reason, response.text)
            return
        else:
            try:
                return response.json()
            except:
                return response.text
    
    #A get request that returns the parameters in json format
    def get(self, url, payload=None):
        return Canvas.toJson(requests.get(url, headers=self.headers, json=payload))
    
    #A post request that returns the parameters in json format
    def post(self, url, payload=None):    
        return Canvas.toJson(requests.post(url, headers=self.headers, json=payload))
    
    #A put request that returns the parameters in json format
    def put(self, url, payload=None):
        return Canvas.toJson(requests.put(url, headers=self.headers, json=payload))
    
    #A delete request that returns the parameters in json format
    def delete(self, url, payload=None):
        return Canvas.toJson(requests.delete(url, headers=self.headers, json=payload))

    #gets the sections within a course
    def getSections(self, payload=None):
        url = self.base_url + 'courses/' + self.courseID + '/sections'
        return self.get(url, payload)
    
    #gets all quizzes and assignments
    def getAllAssignments(self, payload=None):
        quiz_url = self.base_url + 'courses/'+self.courseID+'/quizzes?per_page=100'
        assignment_url = self.base_url + 'courses/'+self.courseID+'/assignments?all_dates=1&per_page=100'
        
        q = self.get(quiz_url, payload)
        a = self.get(assignment_url, payload)
        return q,a
    
    #gets an individual assignment given its ID
    def getAssignment(self, assignmentID, payload=None):
        assignmentID = str(assignmentID)
        url = self.base_url + 'courses/' + self.courseID + '/assignments/' + assignmentID
        return self.get(url, payload)
    
    #creates an individual assignment given parameters
    def makeAssignment(self, payload):
        url = self.base_url + 'courses/' + self.courseID + '/assignments/'
        return self.get(url, payload)
    
    #edits an individual assignment given its ID        
    def editAssignment(self, assignmentID, payload=None):
        assignmentID = str(assignmentID)
        url = self.base_url + 'courses/' + self.courseID + '/assignments/' + assignmentID
        return self.put(url, payload)
    
    #gets a assignment overrides given its ID 
    def getAssignmentOverrides(self, assignmentID, payload=None):
        assignmentID = str(assignmentID)        
        url = self.base_url + 'courses/' + self.courseID + '/assignments/' + assignmentID + '/overrides'
        return self.get(url, payload)

    #creates an assignment override given assignment ID and override info 
    def makeAssignmentOverride(self, assignmentID, payload):
        assignmentID = str(assignmentID)
        url = self.base_url + 'courses/' + self.courseID + '/assignments/' + assignmentID + '/overrides'
        return self.post(url, payload)
    
    #deletes an assignment override given assignment and override IDs
    def deleteAssignmentOverride(self, assignmentID, overrideID, payload=None):
        assignmentID = str(assignmentID)        
        overrideID = str(overrideID)
        url = self.base_url + 'courses/' + self.courseID + '/assignments/' + assignmentID + '/overrides/'+ overrideID
        return self.delete(url, payload)

    #gets an individual quiz given its ID  
    def getQuiz(self, quizID, payload=None):
        quizID = str(quizID)
        url = self.base_url + 'courses/' + self.courseID + '/quizzes/' + quizID
        return self.get(url, payload)
    
    #creates an individual quiz given parameters    
    def makeQuiz(self, quizID, payload):
        url = self.base_url + 'courses/' + self.courseID + '/quizzes/'
        return self.post(url, payload)
    
    #edits an individual quiz given its ID 
    def editQuiz(self, quizID, payload=None):
        quizID = str(quizID)
        url = self.base_url + 'courses/' + self.courseID + '/quizzes/' + str(quizID)
        return self.put(url, payload)
    
    #gets overrides for all quizzes
    def getQuizOverrides(self, payload=None):
        url = self.base_url + 'courses/' + self.courseID + '/quizzes/assignment_overrides'
        return self.get(url, payload)
    
    

class Assignment():
    def __init__(self, name, due_at, ID, overrides, muted, published, unlock_at, lock_at, canvas):
        """
        Creates an assignment object with properties of interest
        """
        self.name = name
        self.due = due_at
        self.id = ID
        self.overrides = overrides
        self.muted = int(muted)
        self.published = int(published)
        self.unlock = unlock_at
        self.lock = lock_at
        self.canvas= canvas
        self.parseOverrides()
        
    #gets course section info for the assignment
    def getSectionInfo(self):
        sections = self.canvas.getSections()
        sections = Assignment.filterData(sections, ['name','id'])
        sectionList = []
        
        for section in sections:
            if 'lab' in section['name'].lower():
                sectionList.append(section)
        
        return sectionList
                
    #formats the overrides in a cohesive manner for processing
    def parseOverrides(self):
        
        #if no overrides, each section takes the due date of the overall
        self.sections={}
        
        secList = self.getSectionInfo()
        for sec in secList:
            self.sections[sec['id']]= {'name':sec['name']}
            
        if self.overrides:
            for override in self.overrides:
                self.sections[override['course_section_id']]['date'] = override['due_at']
                self.sections[override['course_section_id']]['id'] = override['id']
    
    #returns the value of the requested key of the assignment object
    #for dates, if the object is None, then return an empty string
    def get(self, key):
        if type(key) == str:
            if 'name' in key.lower():
                return self.name
            elif 'due' in key.lower():
                if self.due:
                    return self.due
                else:
                    return ''
            elif 'id' == key.lower():
                return self.id
            elif 'override' in key.lower():
                return self.overrides
            elif 'mute' in key.lower():
                return self.muted
            elif 'publish' in key.lower():
                return self.published
            elif 'unlock' in key.lower():
                if self.unlock:
                    return self.unlock
                else:
                    return ''
            elif 'lock' in key.lower():
                if self.lock:
                    return self.lock
                else:
                    return ''
            else:
                print(key)
                raise KeyError
        elif type(key) == int:   
            if key not in self.sections:
                raise KeyError
            try: 
                if self.sections[key]['date']:
                    return self.sections[key]['date']
            except KeyError: 
                if self.due:
                    return self.due
                else:
                    return ''
        else:
            print(key)
            raise KeyError
    
    #deletes all overrides for this assignment
    def deleteOverrides(self):
        for section in self.overrides:
            if 'id' in section:
                self.canvas.deleteAssignmentOverride(self.id, section['id'])
    
    #compares a dictionary of values to the assignment
    def compare(self, other):
        def compareSections(sections):            
            #for each section, make sure it has a date before trying to compare it
            #None and '' mean no date
            try:
                for section in sections:
                    #if the section had no previous due date, ensure the new section has no due date or else return false
                    if 'date' not in self.sections[section]:
                        if sections[section]=='':
                            continue
                        elif sections[section]!='':
                            return False
                    
                    elif self.sections[section]['date'] == None and sections[section] == '':
                        continue
                    elif self.sections[section]['date'] == '' and sections[section] == '':
                        continue 
                    elif self.sections[section]['date'] != sections[section]:
                        return False
                else: return True
            
            except KeyError:
                return False
        
        #will return a dictionary of properties that are not matched
        changes = {'name': True, 'due':True, 'muted':True, 'published':True, 'sections':True, 'lock':True, 'unlock':True}
        
        #go through each key and compare it
        for key in changes:
            if key == 'sections':
                changes[key] = compareSections(other['sections'])
            
            elif key == 'due':
                combined = [self.get(key),other[key]]
                if (None in combined and '' in combined) or len(set(combined))==1: 
                    changes[key] = True
                else:
                    changes[key] = False
            elif self.get(key) != other[key]:
                changes[key]=False
        
        return changes
    
    #this filters out unwanted properties of an assignment
    def filterData(data, data_to_keep):
        for x in range(len(data)):
            #need to create a list of items to delete
            del_items = []
            
            #go through and find the items not required
            for item in data[x]:
                if item not in data_to_keep:
                    del_items.append(item)
            #remove the items not needed
            for item in del_items:
                del data[x][item]
        return data
    
    #Create string representation of the Assignment
    def __repr__(self):
        str_rep = str(self.name) + "\n\tdue_date: \n\t\t" + str(self.due) + "\n\tsections:\n"
        
        #loop through and list sections
        for sect_id in self.sections:
            section = self.sections[sect_id]
            str_rep = str_rep + "\t\t" + section['name'] + "-> "
            #if section has due date, add due date
            if 'date' in section:
                str_rep = str_rep + str(section['date'])
            else:
                str_rep = str_rep + str(None)
            str_rep = str_rep+"\n"
        #add published, lock, and unlock
        str_rep = str_rep + "\tpublished:"+ "\n\t\t" + str(bool(self.published)) +"\n"
        str_rep = str_rep + "\tlock:"+ "\n\t\t" + str(self.lock) +"\n"
        str_rep = str_rep + "\tunlock:"+ "\n\t\t" + str(self.unlock) +"\n"
        
        return str_rep
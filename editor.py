#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 17:45:08 2019

@author: Chris Nguyen
contact: clnguyen2@wisc.edu
"""

import re
import csv
import random
import datetime as dt
from dateutil import tz
from tkinter import Button, Label, Tk, Entry, LabelFrame, Frame
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json


#Custom library for Canvas items and assignments
from CanvasAPI import Canvas, Assignment

#%% Get default hostname, courseID, and token here from json file

hostname = '' #the base url of your canvas page ie. https://canvas.wisc.edu
courseID = '' #course ID
token = '' #token obtained from Canvas

try:
    #load the json file
    json_file = open('defaults.json', 'r')
    defaults = json.load(json_file)
    json_file.close()
    
    #read in default values
    if 'hostname' in defaults:
        hostname = defaults['hostname']
    if 'courseID' in defaults:
        courseID = defaults['courseID']
    if 'token' in defaults:
        token = defaults['token']
except FileNotFoundError:
    pass

#%%
class App():
    """
    Tkinter app for downloading and uploading assignments to Canvas.
    """
    def __init__(self, courseID ='', token =''):
        #Set up the GUI
        self.root=Tk()
        self.root.resizable(width=False, height=False)
        self.root.title("Canvas Assignment Editor")
        self.root.geometry("650x350+30+30")
        self.root.config(borderwidth=4)
        
        #The description on top
        self.label = Label(self.root, text = 'Paste CourseID and Canvas Token below. Press Download to create a TSV file')
        self.label.grid(row=0, column=0, sticky='W')
        self.label = Label(self.root, text = 'TSV is saved to the working directory.')
        self.label.grid(row=1, column=0, sticky='W')
        
        #frame for info
        self.info = LabelFrame(self.root, text = 'Canvas Info')
        self.info.grid(row=2, column = 0, sticky = 'EW')
        
        hostLabel = Label(self.info, text = 'Canvas Hostname')
        hostLabel.grid(row=0, column = 0, sticky = 'W')
        self.host = Entry(self.info, text = '')
        self.host.grid(row = 0, column = 1, sticky='W')
        
        courseLabel = Label(self.info, text = 'Course ID')
        courseLabel.grid(row=1, column = 0, sticky = 'W')
        self.courseID = Entry(self.info, text = '')
        self.courseID.grid(row = 1, column = 1, sticky='W')
        
        tokenLabel = Label(self.info, text = 'Token')
        tokenLabel.grid(row=2, column = 0, sticky = 'W')
        self.token = Entry(self.info, text = '', show="*")
        self.token.grid(row = 2, column = 1, sticky='W')
        
        self.frame = Frame(self.root)
        self.frame.grid(row=3, column=0, sticky = 'EW')
        
        #Download Frame
        self.load= LabelFrame(self.frame, text = 'Download')
        self.load.grid(row =0, column = 0, sticky = 'EW')
        
        #Download button
        downloadButton = Button(self.load, text = 'Download Assignments', command = self.loadCanvas)
        downloadButton.grid(row=0, column=0, sticky = 'EW')
        self.download_file = Label(self.load, text = '', fg = 'red')
        self.download_file.grid(row=1, column = 0)
                
        #Upload Frame
        self.upload= LabelFrame(self.frame, text = 'Upload')
        self.upload.grid(row =0, column = 1, sticky = 'EW')
        
         #Save as file name entry box
        loadFileLabel = Button(self.upload, text = 'TSV file to upload', command = self.sendFile)
        loadFileLabel.grid(row=0, column=0, sticky='W')
        self.upload_file = Label(self.upload, text='', fg='red')
        self.upload_file.grid(row=1, column = 0, sticky = 'EW')
        
        #Label for feedback once done
        self.label = Label(self.root, text = '', fg = 'red')
        self.label.grid(row=4,column=0)
        
        #populates the host, token, and courseID if they are values
        try: self.host.insert(0, hostname.strip())
        except: pass
        try: self.courseID.insert(0, courseID.strip())
        except:pass
        try: self.token.insert(0, token.strip())
        except:pass
        
        #Starts the app
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)        
        self.root.mainloop()        
        
        
    #function to ensure course id and token are populated
    def validateInfo(self):
         if self.courseID.get().strip() and self.token.get().strip():
             return True
         else:
             self.label["text"] = 'Please fill out course ID and token information'
             return False
        
    #function to send TSV file to Canvas
    def sendFile(self):
        if not self.validateInfo():
            return
        self.root.update()
        self.label["text"] = 'Uploading... Please Wait'
        filename = askopenfilename(title = "Select file", filetypes = (("tab-separated values","*.tsv"),("all files","*.*")))
        if filename == None or filename =='': # asksaveasfile return `None` if dialog closed with "cancel".
            self.label["text"] = ''    
            return
        self.upload_file['text']=filename[filename.rfind('/')+1:]
        self.root.update()
        try: 
            upload(self.host.get(), self.courseID.get(), self.token.get(), filename)
            self.label['text'] = 'Upload complete. Check Canvas'
            self.upload_file['text'] = ''
        except: 
            self.label["text"] = 'Error... Check console for messages'
            self.upload_file['text'] = ''
            raise
        
    #function to load Canvas assignments and save to TSV
    def loadCanvas(self):
            if not self.validateInfo():
                return
            self.root.update()
            self.label["text"] = 'Downloading... Please Wait'
            filename = asksaveasfilename(title = 'File to save Canvas data', defaultextension=".tsv", filetypes = (("tab-separated values","*.tsv"),("all files","*.*")))
            if filename == None or filename =='': # asksaveasfile return `None` if dialog closed with "cancel".
                self.label["text"] = ''
                return
            self.download_file['text'] = filename[filename.rfind('/')+1:]
            self.root.update()
            try: 
                download(self.host.get(), self.courseID.get(),self.token.get(),filename)
                self.label["text"] = 'Done. File saved to ' + self.download_file['text']
                self.download_file['text'] = ''
            except: 
                self.label["text"] = 'Error... Check console'
                self.download_file['text'] = ''
                raise
            
            
    #needed for clean exit of program
    def on_close(self):
        self.root.destroy()
        exit(0)
    
    
#%%

#Converts local time to iso format to upload to canvas
def local_to_iso(date_time):
    if date_time == '' or date_time == None or date_time == 'None':
        return ''
    
     #if the pattern already matches iso, return it
    pattern = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'
    if re.match(pattern, date_time):
        return date_time
    
    from_zone = tz.tzlocal() #convert from local timezone
    to_zone = tz.tzutc() #convert to utc timezone
    
    #Try a bunch of different variations of the timestamp
    try: 
        date_in = dt.datetime.strptime(date_time, '%m/%d/%Y %H:%M:%S')
    except ValueError:
        try:
            date_in = dt.datetime.strptime(date_time, '%m/%d/%Y %H:%M')
        except ValueError:
            try:
                date_in = dt.datetime.strptime(date_time, '%m/%d/%y %H:%M:%S')
            except ValueError:
                try:
                    date_in = dt.datetime.strptime(date_time, '%m/%d/%y %H:%M')
                except ValueError:
                    print(type(date_time), date_time)
    
    date_in = date_in.replace(tzinfo=from_zone)
    date_out = date_in.astimezone(to_zone)
    
    #if the minute is at 59, make it 59 seconds
    if date_out.minute == 59: 
        date_out = date_out.replace(second = 59)
    
    return date_out.strftime('%Y-%m-%dT%H:%M:%SZ') #returns time in ISO format

#Converts iso time to standard format for the spreadsheet
def iso_to_local(date_time):
    if date_time == '' or date_time == None or date_time.lower() == 'None':
        return ''
    
    #if the pattern already matches local, return it
    pattern = '[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]+ [0-9][0-9]?:[0-9][0-9]:[0-9][0-9]'
    pattern2 = '[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]+ [0-9][0-9]?:[0-9][0-9]'
    if re.match(pattern, date_time) or re.match(pattern2, date_time):
        return date_time
    
    from_zone = tz.tzutc() #convert from utc
    to_zone = tz.tzlocal() #convert to local timezone
    
    date_in = dt.datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%SZ')
    date_in = date_in.replace(tzinfo=from_zone)
    date_out = date_in.astimezone(to_zone)
    
    return date_out.strftime('%m/%d/%Y %H:%M:%S')



def getCourseAssignments(canvas):
    """
    Gets the assignments from Canvas
    
    params:
        canvas: a Canvas object
    """
    
    print('Getting assignments...', end='')
    quizzes, assignments = canvas.getAllAssignments()
    print(' Done')
    print('Making assignment objects...', end='')
    
    #filter out the properties from the canvas assignments
    keepList = ['id','title','due_at', 'all_dates', 'unlock_at', 'lock_at', 
                'show_correct_answers_at', 'hide_correct_answers_at', 'published', 
                'muted', 'name', 'is_quiz_assignment']
    
    assignments = Assignment.filterData(assignments, keepList)
    
    #add overrides to assignment 
    for assignment in assignments:
        overrides = canvas.getAssignmentOverrides(assignment['id'])
        overrides = Assignment.filterData(overrides, ['id', 'due_at', 'course_section_id', 'title'])
        remove_list = []
        for override in overrides:
            if 'lab' not in override['title'].lower():
                remove_list.append(override)
        for override in remove_list:
            overrides.remove(override)
        assignment['overrides'] = overrides
    
    #create a list of assignment objects
    assignmentList=[]
    
    #create an assignment object for each assignment
    for a in assignments:
        assignmentList.append(Assignment(a['name'], a['due_at'], a['id'], a['overrides'], a['muted'], a['published'], a['unlock_at'], a['lock_at'], canvas))
    
    print(' Done')
    return assignmentList

def download(hostname, courseID, token, filename):
    """
    Downloads and creates a TSV for Canvas Assignments
    """
    #Function that actually creates the TSV
    def create_Canvas_TSV(canvas, assignmentList, filename):
        print('Creating TSV...', end='')
    
        sections = canvas.getSections()
        sections = Assignment.filterData(sections, ['name','id'])
        
        sectionNames = []
        sectionKeys = []
        for section in sections:
            if 'lab' in section['name'].lower():
                sectionNames.append(section['name'])
                sectionKeys.append(section['id'])
        
        #Create the headers
        headers = sectionNames
        headers.insert(0, "Title")
        headers += ["Available from", "Available until", "Published", "Muted", "Canvas ID"]
        
        #create a key for each header
        keys = sectionKeys
        keys.insert(0, 'name')
        keys +=['unlock_at', 'lock_at','published', 'muted','id']
        
        headerKeys= {}
        for x in range(len(headers)):
            headerKeys[headers[x]] = keys[x]
        
        #this is the pattern for a date
        datetime_pattern = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'
        
        #Add headers
        string = ''
        for header in headers:
            string+=header +"\t"
        string = string[:-1]+'\n'
        
        #add the asisgnments
        for assignment in assignmentList:
            for header in headers:
                addition = str(assignment.get(headerKeys[header]))
                if addition.lower() == 'none':
                    addition = ''
                if re.search(datetime_pattern, addition):
                    addition = iso_to_local(addition)
                string+= addition + '\t'
            string = string[:-1]+'\n'
        
        #write everything to a file
        with open(filename,'w') as file:
            file.write(string)
        print('Done')
    
    #create Canvas object to interface with Canvas
    canvas = Canvas(hostname, courseID, token)
    
    #get the course assignments and then sort the list by the due dates and then write to TSV
    assignments = getCourseAssignments(canvas)
    random_section = random.choice(list(assignments[0].sections.keys()))
    assignments.sort(key=lambda assignment: assignment.get(random_section), reverse=False)
    create_Canvas_TSV(canvas, assignments, filename)

def upload(hostname, courseID, token, filename):
    """
    Uploads a TSV file with Canvas assignments to Canvas
    """
    
    def getHeaders(row):
        headerCol = {}
        for idx, entry in enumerate(row):
            headerCol[entry] = idx
    
        return headerCol
    
    #Create Canvas object to interface with Canvas
    canvas = Canvas(hostname, courseID, token)
    
    #Get all the old assignments and create a dictionary to access them
    oldAssignments = getCourseAssignments(canvas)
    oldDict = {}
    
    print('Uploading new Assignments...')
    for assignment in oldAssignments:
        oldDict[assignment.id]=assignment
    
    #read in the file
    with open(filename) as tsvfile:
        data = csv.reader(tsvfile, delimiter='\t')
        
        #finds the headers
        headerCol = getHeaders(next(data))

        #finds the headers for individual sections        
        sections = canvas.getSections()
        sectionDict = {}
        for section in sections:
            if 'lab' in section['name'].lower():
                sectionDict[section['id']] = section['name']
        
        sectionHeaders = {}
        for idx, header in enumerate(headerCol):
            for section in sections:
                if section['name'] in header:
                    sectionHeaders[section['id']] = idx
                    break
        
        #update section headers into the headerCols dictionary
        headerCol.update(sectionHeaders) 
    
        newAssignments ={}
        
        for idx, row in enumerate(data):            
            #get the section due dates and save them individually
            section_due_dates = {}
            for section in sectionDict:
                section_due_dates[section]=local_to_iso(row[headerCol[section]])
                
            #if all the section due dates are the same, set the due_date to the same, otherwise, don't have a valid due date
            if len(set(section_due_dates.values())) <= 1:
                due_date = str(list(section_due_dates.values())[0]) 
                
                #remove all section due dates since they are all the same
                for section in section_due_dates:
                    section_due_dates[section] = '' 
                single_due_date = True
            else:
                due_date = ''
                single_due_date = False
                
            
            #create a dictionary for the newly updated section from canvas
            newAssignment = {'name': str(row[headerCol['Title']]), 'due': local_to_iso(due_date), 'muted': bool(int(row[headerCol['Muted']])), 'published':bool(int(row[headerCol['Published']])), 'sections':section_due_dates, 'lock':local_to_iso(row[headerCol['Available until']]), 'unlock':local_to_iso(row[headerCol['Available from']])}
            
            #compare the new assignment with the new assignment
            oldAssignment = oldDict[int(row[headerCol['Canvas ID']])]
            comp = oldAssignment.compare(newAssignment)
            
            newAssignments[oldAssignment.id]=newAssignment #makes a dictionary of changes for easy debugging
            
           #if anything is different in new assignment, update the assignment
            if False in comp.values():
                #delete all overrides so you can make new ones
                oldAssignment.deleteOverrides()                                                                                                                                                           
                
                #make a new override for each section
                for section in oldAssignment.sections:
                    if not single_due_date and section_due_dates[section] != None and section_due_dates[section] !='':
                        payload = {'assignment_override':{'course_section_id': section, 'due_at': section_due_dates[section], 'lock_at': newAssignment['lock'], 'unlock_at': newAssignment['unlock']}}
                        if canvas.makeAssignmentOverride(oldAssignment.id, payload) == None: #prints error message if nothing returned
                            print('--> Assignment: "'+oldAssignment.name + '" due date for section "' + oldAssignment.sections[section]['name'] + '" not updated')                 
                #update the whole assignment
                payload = {'assignment':{'name':newAssignment['name'], 'due_at':newAssignment['due'], 'muted':newAssignment['muted'], 'published':newAssignment['published'], 'lock_at': newAssignment['lock'], 'unlock_at': newAssignment['unlock']}}
                canvas.editAssignment(oldAssignment.id, payload)
                print('Assignment updated:', oldAssignment.name)
        print('Done')
        return newAssignments, oldDict

#%% Main section of code that runs
if __name__ == '__main__':
    app = App(courseID, token)


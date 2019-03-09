# Tkinter based GUI to download and edit Canvas assignments for a specific course.

## Instructions
The following are required to run the program: Canvas Hostname, Canvas Course ID, Account Access Token.

1. The Canvas Hostname is taken from your homepage of Canvas page: ie. for UW-Madison, https://canvas.wisc.edu/

2. Get Canvas Course ID from Canvas. The Course ID can be found in the url of the course page: https://canvas.wisc.edu/courses/:courseid

3. Create an access token by going to your account -> settings. On the settings page, click the tab that says "+New Access Token". Follow the prompts and then copy down the access token.

4. Enter this information into a `defaults.json` file. A template file is provided.


## Running the Program
Requires Python 3 and utilizes the Tkinter library.
`python editor.py`

1. Insert the Canvas Hostname, Course ID, and token into the respective text entry boxes on the GUI.

2. Downloading requires you to create a new tsv file or overwrite an existing one. Supply the prompt with a valid filename and click ok. Once downloaded, the course content is saved into the TSV file.

3. Edit the TSV to the desired due dates and settings. DO NOT modify the Canvas ID for any assignment. Save the TSV file when finished.

4. Upload the modified information by clicking upload and selecting the saved TSV file and waiting for the prompt to finish.

## Contact

If you have questions, email clnguyen2@wisc.edu or create an issue on GitHub.

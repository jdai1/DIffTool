# DIffTool

## Contents
- [Description](#description)
- [Logic](#logic)
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)

## Logic
The DiffTool is the backend logic that compares database dumps in the form of excel files, A and B. A represents a previous data dump marked up by a human, while
B represents a recent "raw" data dump. The resulting comparison records and performs changes from A to B, outputting the resulting information in a excel file R.
Then, R will represent A in following comparisons. Multiple files can be compared with the DiffTool by specifying files in the config.ini file. The assumption is 
that each A and B file pair will have the same name (some_file_name.xlsx), located in different folders. All "A" files will exist in wip folders (work in 
progress) while all "B" files will exist in stock folders (data dump). To compare files, select a older wip folder and newer stock folder. The files specified in 
the config.ini file will then be compared and stored in the wip folder of the stock folder invovled in the comparison. 

### Example Tree Structure
![FileManager View](https://github.com/jdai1/DIffTool/blob/master/ScreenShots/FileManager.png)

The name of each top level folder represents a date-time, which are created with wip and stock folders simultaneously. Therefore, the stock folder in a compariosn must exist in a newer folder than the folder containing tehw ip files.

Eg. 2010601 wip × 20190701 stock -> resulting files placed in 20190701 wip

## Description
> A flask web app utilizing bootstrap-treeivew and jquery file upload to provide interactive management of directories and files. Supports file upload and  
> download,creation/deletion of directories, and of course, DiffTool comparisons. The app also includes a status log which records actions such as additions, 
> deletions, or comparisons. Styled with bootstrap and functionality provided by jQuery.

## Features
[jQuery-File-Upload](https://github.com/blueimp/jQuery-File-Upload)

- **Multiple file upload:**  
  Allows to select multiple files at once and upload them simultaneously.
- **Drag & Drop support:**  
  Allows to upload files by dragging them from your desktop or file manager and
  dropping them on your browser window.
- **Upload progress bar:**  
  Shows a progress bar indicating the upload progress for individual files and
  for all uploads combined.
- **Cancelable uploads:**  
  Individual file uploads can be canceled to stop the upload progress.
- **Resumable uploads:**  
  Aborted uploads can be resumed with browsers supporting the Blob API.
- **Chunked uploads:**  
  Large files can be uploaded in smaller chunks with browsers supporting the
  Blob API.
- **Client-side image resizing:**  
  Images can be automatically resized on client-side with browsers supporting
  the required JS APIs.
- **Preview images, audio and video:**  
  A preview of image, audio and video files can be displayed before uploading
  with browsers supporting the required APIs.
- **No browser plugins (e.g. Adobe Flash) required:**  
  The implementation is based on open standards like HTML5 and JavaScript and
  requires no additional browser plugins.
- **Graceful fallback for legacy browsers:**  
  Uploads files via XMLHttpRequests if supported and uses iframes as fallback
  for legacy browsers.
- **HTML file upload form fallback:**  
  Allows progressive enhancement by using a standard HTML file upload form as
  widget element.
- **Cross-site file uploads:**  
  Supports uploading files to a different domain with cross-site XMLHttpRequests
  or iframe redirects.
- **Multiple plugin instances:**  
  Allows to use multiple plugin instances on the same webpage.
- **Customizable and extensible:**  
  Provides an API to set individual options and define callback methods for
  various upload events.
- **Multipart and file contents stream uploads:**  
  Files can be uploaded as standard "multipart/form-data" or file contents
  stream (HTTP PUT file upload).
- **Compatible with any server-side application platform:**  
  Works with any server-side platform (PHP, Python, Ruby on Rails, Java,
  Node.js, Go etc.) that supports standard HTML form file uploads.

Treeview (Features added onto original bootstrap-treeview)
- **Expand/Collapse on click:**
  Directories can be collapsed and expanded on click.
- **Live update:**
  Responsive to file and directory changes, updating after such events.
- **Interactive Display:**
  Displays files of directory within jquery file upload widget, promoting quick
  and simple file uploads, downloads, and deletions.
 
DiffTool Validation

Status

## Requirements

- [jQuery](https://jquery.com/) v 3.5.1+
- [jQuery Iframe Transport plugin](https://github.com/blueimp/jQuery-File-Upload/blob/master/js/jquery.iframe-transport.js).    
- [jQuery UI widget factory](https://api.jqueryui.com/jQuery.widget/). 

 - [Bootstrap 3](https://getbootstrap.com/docs/3.3/)   **NOT BOOTSTRAP 4**

**Included in virtual env**

- simplejson
- flask
- Pillow Image
- shutil
- traceback
- configparser
- platform

## Setup
Clone the github repository
```sh
git clone https://github.com/jdai1/DIffTool.git
```

Activate the virtual environment
```sh
source env/bin/activate
```

Then to run the app
```sh
python3.8 app/app.py
```
### Local Changes
In app.py, several variables can be modified to best suit certain circumstances.
```python
app.config['THUMBNAIL_FOLDER'] = '/UI/app/static/local/thumbnail'
app.config['ROOT_FOLDER'] = '/Input'
app.config['PORT'] = 3000
app.config['DEBUG'] = True
```
- THUMBNAIL FOLDER - the location of the thumbnails that appear on the file upload widget
- ROOT_FOLDER - the location of the directories and files that the file tree displays
- PORT - the port that the local host runs on
- DEBUG - the state in which the app runs (Debug=True means http requests are shown and errors are displayed)

```python
ALLOWED_EXTENSIONS = set(['txt', 'gif', 'png', 'jpg', 'jpeg', 'bmp', 'xlsx', 'rar', 'zip', '7zip', 'doc', 'docx'])
IGNORED_FILES = set(['.gitignore', '.DS_Store'])
```
- ALLOWED EXTENSIONS - the extensions of files allowed to be uploaded
- IGNORED FILES - files that are ignored when displaying files in the tree view

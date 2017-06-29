import os
import sys
import json
from flask import Flask, request, redirect, url_for, send_from_directory, Request, flash
from werkzeug.utils import secure_filename
from S3Uploader import uploader
#import ImageAnalysis

#Path to upload folder and the allowed types of files that can be uploaded
UPLOAD_FOLDER = '/Users/Autodesk/Desktop/upload_folder'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#Check if the file extension type is valid
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #Check that the file is given in the post request
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        #If user does not select a file
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        #Save file locally to UPLOAD_FOLDER
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #Receive parameters from user
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            parameters = eval(request.form['json'])

            return uploader(path, parameters)



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0')
    except:
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)

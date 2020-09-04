# flask
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, abort

# firebase
import firebase_admin
import pyrebase
from firebase_admin import credentials, auth

# standard python lib
import os
import json
import shutil
import ast
import time
from collections import OrderedDict
import traceback
from configparser import ConfigParser
import platform
import urllib3
from urllib3.exceptions import HTTPError

# imported modules
from lib.uploadfile import uploadfile
from lib.DiffTool import compareTool
from lib.treeview import treeview
from PIL import Image
import simplejson
from functools import wraps

app = Flask(__name__)

app.config['THUMBNAIL_FOLDER'] = '/Users/Julian/Documents/Numedi-Internship/2020/Excel Compare Tool UI/app/static/local/thumbnail'
app.config['ROOT_FOLDER'] = '/Users/Julian/Documents/Numedi-Internship/2020/Excel Compare Tool/Input'
app.config['CURRENT_FOLDER'] = app.config['ROOT_FOLDER']
app.config['PORT'] = 3000
app.config['DEBUG'] = True
app.config['EVENTS'] = {}
app.config['INDEX'] = 0
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['TRAP_HTTP_EXCEPTIONS']=True


app.secret_key = '53a9d4e6ab6c9375fd9cd79a4afacb2a7670e0c01cc41190'


ALLOWED_EXTENSIONS = set(['txt', 'gif', 'png', 'jpg', 'jpeg', 'bmp', 'xlsx', 'rar', 'zip', '7zip', 'doc', 'docx'])
IGNORED_FILES = set(['.gitignore', '.DS_Store'])


def addEvent(message):
    app.config['EVENTS'][str(app.config['INDEX'])] = message
    app.config['INDEX'] += 1


def genFileName(filename):
    return os.path.join(app.config['CURRENT_FOLDER'], filename)


def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def existingFile(filename):
    return os.path.exists(os.path.join(app.config['CURRENT_FOLDER'], filename))


def create_thumbnail(image):
    try:
        base_width = 80
        img = Image.open(os.path.join(app.config['CURRENT_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))
        return True
    except:
        print(traceback.format_exc())
        return False


def get_treeview(type):
    tv = treeview(app.config['ROOT_FOLDER'])
    result = tv.get_view(type)
    return simplejson.dumps(result)


def post(files):
    if files:
        output = ""
        for file in files:
            filename = file.filename
            mime_type = file.content_type

            if not allowedFile(file.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
            elif existingFile(file.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File already exists")
            else:
                # save file to disk
                uploaded_file_path = genFileName(filename)
                file.save(uploaded_file_path)

                # create thumbnail after saving
                if mime_type.startswith('image'):
                    create_thumbnail(filename)

                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
            output += simplejson.dumps({"files": [result.get_file()]})
        return output


def get():
    # get all file in ./data directory
    files = [f for f in os.listdir(app.config['CURRENT_FOLDER']) if os.path.isfile(os.path.join(app.config['CURRENT_FOLDER'], f)) and f not in IGNORED_FILES ]
    file_display = []
    for f in files:
        size = os.path.getsize(os.path.join(app.config['CURRENT_FOLDER'], f))
        file_saved = uploadfile(name=f, size=size)
        file_display.append(file_saved.get_file())

    return simplejson.dumps({"files": file_display})


def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not request.headers.get('authorization'):
            print('no authorization')
            return redirect(url_for('user'))
        try:
            user = auth.verify_id_token(request.headers['authorization'], check_revoked=True)
            pb_auth.current_user = user
            print('successful')
        except:
            print('invalid')
            return redirect(url_for('user'))
        return f(*args, **kwargs)
    return wrap


@app.route('/FileManager/')
def fileManager():
    data = get_treeview('view')
    return render_template('FileManager.html', data=data)


@app.route('/FileManager/upload/<string:request_path>', methods=['GET', 'POST'])
@app.route('/FileManager/upload', methods=['GET', 'POST'])
@check_token
def upload(**options):
    # root folder
    if len(options) == 1:
        request_path = options['request_path']
        fixed_path = '/'
        for s in request_path:
            if s == '|':
                fixed_path += '/'
            else:
                fixed_path += s
        app.config['CURRENT_FOLDER'] = app.config['ROOT_FOLDER'] + fixed_path
        addEvent(fixed_path + ' was accessed')
        if request.method == 'POST':
            files = request.files.getlist('file[]')
            file_names = []
            for file in files:
                file_names.append(file.filename)
            if len(file_names) == 1:
                addEvent(str(file_names) + ' was added to ' + fixed_path)
            else:
                addEvent(str(file_names) + ' were added to ' + fixed_path)
            return post(files)
        if request.method == 'GET':
            return get()
        return redirect(url_for('FileManager.html'))
    else:
        addEvent('Root folder accessed')
        app.config['CURRENT_FOLDER'] = app.config['ROOT_FOLDER']
        if request.method == 'POST':
            files = request.files.getlist('file[]')
            return post(files)
        if request.method == 'GET':
            return get()
        return redirect(url_for('FileManager.html'))


@app.route("/FileManager/delete/<string:filename>", methods=['DELETE'])
@check_token
def delete(filename):
    file_path = os.path.join(app.config['CURRENT_FOLDER'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)
            addEvent(filename + ' was successfully removed')
            return simplejson.dumps({filename: 'True'})
        except:
            addEvent('An error occurred when ' + filename + ' was being removed')
            return simplejson.dumps({filename: 'False'})


@app.route("/FileManager/action_folder/<string:dirname>", methods=['GET'])
@check_token
def action_folder(dirname):
    print(dirname)
    action = request.args['action']
    if action == 'delete':
        addEvent('Directory: ' + dirname + ' was successfully deleted')
        shutil.rmtree(os.path.join(app.config['ROOT_FOLDER'], dirname))
        return get_treeview('view')
    if action == 'add':
        addEvent('Directory: ' + dirname + ' was successfully added')
        os.mkdir(os.path.join(app.config['ROOT_FOLDER'], dirname))
        os.mkdir(os.path.join(app.config['ROOT_FOLDER'], dirname, 'wip'))
        os.mkdir(os.path.join(app.config['ROOT_FOLDER'], dirname, 'stock'))
        return get_treeview('view')
    addEvent('An error occurred when ' + dirname + 'was being deleted/added')
    return 'hello' #redirect(url_for('fileManager'))


@app.route("/FileManager/thumbnail/<string:filename>", methods=['GET'])
@check_token
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename=filename)


@app.route("/FileManager/data/<string:filename>", methods=['GET'])
@check_token
def get_file(filename):
    return send_from_directory(os.path.join(app.config['CURRENT_FOLDER']), filename=filename)


@app.route("/<string:loc>/update_treeview", methods=['GET'])
@check_token
def update_treeview(**loc):
    return get_treeview(request.args['type'])


@app.route('/<string:loc>/expand_nodes', methods=['GET'])
@check_token
def expand_nodes(**loc):
    # args = list of tags to identify nodes that need to be expanded
    data = simplejson.loads(request.args['data'])
    to_expand = simplejson.loads(request.args['expand'])
    expanded = []
    get_expanded(data, to_expand, expanded)
    return simplejson.dumps(expanded)

# data = treeview
# to_expand = nodes that were previously expanded
# expanded = list of nodes that need to be expanded
def get_expanded(data, to_expand, expanded):
    if not data:
        return
    for i in range(0, len(data)):
        if 'nodes' in data[i].keys():
            directory = data[i]
            path = directory['tags'][0]
            if path in to_expand and directory not in expanded:
                expanded.append(directory)
            get_expanded(directory['nodes'], to_expand, expanded)


@app.route('/DiffTool/')
def diffTool():
    data = get_treeview('tool')
    return render_template('DiffTool.html', data=data)


@app.route('/DiffTool/compare', methods=['GET'])
@check_token
def compare():
    wip_path = app.config['ROOT_FOLDER'] + request.args['wip_path']
    stock_path = app.config['ROOT_FOLDER'] + request.args['stock_path']
    wip_stat = os.stat(wip_path)
    stock_stat = os.stat(stock_path)
    if platform.system() == 'Darwin':
        if round(time.time() - wip_stat.st_birthtime, 3) > round(time.time() - stock_stat.st_birthtime, 3):
            addEvent(wip_path + ' and ' + stock_path + ' were successfully compared.')
            info, files = get_config()
            compareTool(wip_path, stock_path, info, files)
            return get_treeview('tool')
        return 'TIME'
    elif platform.system() == 'Windows':
        if time.time() - wip_stat.st_ctime > time.time() - stock_stat.st_ctime:
            addEvent(wip_path + ' and ' + stock_path + ' were successfully compared.')
            info, files = get_config()
            compareTool(wip_path, stock_path, info, files)
            return get_treeview('tool')
        return 'TIME'
    return 'ERROR'


def get_config():
    config = ConfigParser()
    p = '/Users/Julian/Documents/Numedi-Internship/2020/Excel Compare Tool UI/app/config.ini'
    config.read(p)
    sections = config.sections()
    info = OrderedDict()
    for section in sections:
        section_info = (ast.literal_eval(config[section]['keys']), ast.literal_eval(config[section]['contents']))
        info[section] = section_info
    return info, sections


@app.route('/Status/')
def status():
    events = simplejson.dumps(app.config['EVENTS'])
    return render_template('Status.html', events=events)


@app.route('/Status/clear_events', methods=['GET'])
@check_token
def clear_events():
    app.config['EVENTS'] = {}
    return 'cleared'


cred = credentials.Certificate('/Users/Julian/Documents/Numedi-Internship/2020/Excel Compare Tool UI/app/fbAdminConfig.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('/Users/Julian/Documents/Numedi-Internship/2020/Excel Compare Tool UI/app/fbconfig.json')))
pb_auth = pb.auth()

@app.route('/')
@app.route('/User/')
def user():
    # render login template form
    return render_template('Login.html')


@app.route('/User/login', methods=['POST'])
def login():
    # log in user: return auth token
    email = request.form.get("email")
    password = request.form.get("password")
    if email is None or password is None or email is '' or password is '':
        flash('Error missing field', 'danger')
        return 'Error'
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return jwt
    except:
        flash('An error has occurred while signing in', 'danger')
        return 'Error'


@app.route('/User/redirect', methods=['GET'])
@check_token
def redirect_to_home():
    return url_for('fileManager')


@app.route('/User/logout', methods=['GET'])
def logout():
    if pb_auth.current_user:
        uid = pb_auth.current_user['user_id']
        auth.revoke_refresh_tokens(uid)
    return render_template('Login.html')


@app.errorhandler(403)
def page_not_found(e):
    print('reee')
    print(redirect(url_for('user'), 403))
    return redirect(url_for('user')), 403


@app.route('/Test', methods=['GET'])
def test():
    return redirect(url_for('user'))


if __name__ == '__main__':
    app.run(host='localhost', port=app.config['PORT'], debug=app.config['DEBUG'], threaded=True)


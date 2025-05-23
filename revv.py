import importlib
import spacy
import io, os
from flask import Flask, render_template, request, session, Response, flash, url_for, redirect,make_response
from spacy import displacy


# Get the list of spacy models available
LIST_MODELS = list(spacy.info()['pipelines'].keys())[::-1]

# Import the models available
try:
    importlib.import_module(*LIST_MODELS)
except:
    print("Some models are not available.  Check if they are installed.")

app = Flask(__name__, template_folder = "./HTML", static_folder = "./Static")

UPLOAD_FOLDER = "Static/Uploads/"   

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

app.secret_key = 'REVV_SECRET_KEY'

# Session variables (the Model in MVC)
HELPLINES = """
<h2>Welcome to the Revv Power Reader</h2>
<p>Revv powers your reading by highlighting named entities of your choice.  
This helps you focus on relevant parts and skim over the rest.</p>

To get started:

<ol><li>Browse a file and click Upload.</li>
<li>Choose a model for generating entity list and click Submit.</li>
<li>Choose entities from entity list and click Refresh.</li></ol><br>
<p>Your text is now ready for power reading!</p>
"""

import random
import string

# sessions dictionary where keys are session ids and values are session data

sessions_dict = {}

newkey = lambda n: ''.join(random.choices(string.digits+string.ascii_lowercase+string.ascii_uppercase, k=n))

@app.route("/",methods=["GET","POST"])
def show_mainpage():
    '''The Controller for MVC.'''
    
    global sessions_dict
    """session management: All 'session' variables including session key are stored as cookies.
    Only the doc object and the file lines are stored as part of the global sessions dict."""

    newkey = lambda n: ''.join(random.choices(string.digits+string.ascii_lowercase+string.ascii_uppercase, k=n))
    # Initialize all session variables (the model) in the GET request
    # also get a new session key
    if request.method == "GET":
        session.permanent = True
        session['key'] = newkey(5)  # Get a session key
        sessions_dict[session['key']] = \
            {'doc':None, 'lines':None, 'u_file':None, 'lines_rendered':None} # init a session object

        sessions_dict[session['key']]['lines'] = HELPLINES
        session['rb_option'] = None

        session['list_entities'] = []
        session['cb_options'] = None
        session['doc'] = None

    sessions_dict[session['key']]['lines_rendered'] = "<p>"+sessions_dict[session['key']]['lines']+"</p>"

    if request.method == "POST":
        if request.form.get("submit") == "Upload":
            sessions_dict[session['key']]['u_file'] = request.files['file']                #reads hidden form field
            if sessions_dict[session['key']]['u_file']:
                session['fqfn'] = os.path.join(UPLOAD_FOLDER+sessions_dict[session['key']]['u_file'].filename)
                sessions_dict[session['key']]['u_file'].save(session['fqfn'])
                with open(session['fqfn'],'r') as f:
                    sessions_dict[session['key']]['lines'] = f.read()
                os.unlink(session['fqfn'])  # Cleanup the Upload folder of your uploaded file

                sessions_dict[session['key']]['lines_rendered'] = "<p>"+sessions_dict[session['key']]['lines']+"</p>"

        elif request.form.get("submit") == "Select":
            
            session['rb_option'] = request.form['select_model']  

            if session['rb_option'] in LIST_MODELS:
                nlp = spacy.load(session['rb_option'])
                ner = nlp.get_pipe("ner")
                session['list_entities'] = list(ner.labels)
                # Create doc object and store it as a session variable
                sessions_dict[session['key']]['doc'] = nlp(sessions_dict[session['key']]['lines'])
                
            session['cb_options'] = request.form.getlist('entity')
            

        elif request.form.get("submit") == "Refresh":
            
            session['cb_options'] = request.form.getlist('entity')
            if sessions_dict[session['key']]['doc'] != None:  # Ensure you have a model selected
                sessions_dict[session['key']]['lines_rendered'] = displacy.render(sessions_dict[session['key']]['doc'], style="ent",options={"ents":session['cb_options']})
            else:
                print("You haven't selected a model.  Select a model and then click Refresh.")
    
    # The View
    return render_template('revv.html', file_lines=sessions_dict[session['key']]['lines_rendered'], rb_option=session['rb_option'], list_models=LIST_MODELS, cb_options=session['cb_options'], list_entities=session['list_entities'])  

if __name__ == "__main__":
    app.run()  #(host="0.0.0.0",port=8080)
    exit()
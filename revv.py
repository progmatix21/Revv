import importlib
import spacy
import io, os
from flask import Flask, render_template, request, Response, flash, url_for, redirect
from spacy import displacy

# Get the list of spacy models available
list_models = list(spacy.info()['pipelines'].keys())[::-1]

# Import the models available
try:
    importlib.import_module(*list_models)
except:
    print("Some models are not available.  Check if they are installed.")

app = Flask(__name__, template_folder = "./HTML", static_folder = "./Static")

UPLOAD_FOLDER = "Static/Uploads/"   

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

# Globals (the Model in MVC)
helplines = """
<h2>Welcome to the Revv Power Reader</h2>
<p>Revv powers your reading by highlighting named entities of your choice.  
This helps you focus on relevant parts and skim over the rest.</p>

To get started:

<ol><li>Browse a file and click Upload.</li>
<li>Choose a model for generating entity list and click Submit.</li>
<li>Choose entities from entity list and click Refresh.</li></ol><br>
<p>Your text is now ready for power reading!</p>
"""

lines = helplines

nlp = None


if list_models != []:
    rb_option = list_models[0]
else:
    rb_option = None


list_entities = []

if list_entities != []:
    cb_options = list_entities[0]
else:
    cb_options = None

def delete_folder_contents(folder_to_delete):
    '''Function to clear the Uploads folder.'''
    with os.scandir(folder_to_delete) as entries:
        for entry in entries:
            if entry.is_dir():
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)


@app.route("/",methods=["GET","POST"])
def show_mainpage():
    '''The Controller for MVC.'''
    global lines
    global rb_option
    global cb_options
    global list_entities
    global nlp
    lines_rendered = "<p>"+lines+"</p>"

    if request.method == "POST":
        if request.form.get("submit") == "Upload":
            u_file = request.files['file']                #reads hidden form field
            if u_file.filename:
                delete_folder_contents(UPLOAD_FOLDER)
                fqfn = os.path.join(UPLOAD_FOLDER+u_file.filename)
                u_file.save(fqfn)
                with open(fqfn,'r') as f:
                    lines = f.read()
                lines_rendered = "<p>"+lines+"</p>"

        elif request.form.get("submit") == "Select":
            
            rb_option = request.form['select_model']  

            if rb_option in list_models:
                nlp = spacy.load(rb_option)
                print(f"{rb_option} is selected.")
                ner = nlp.get_pipe("ner")
                list_entities = list(ner.labels)
                
            print(list_entities)
            cb_options = request.form.getlist('entity')

        elif request.form.get("submit") == "Refresh":
            
            cb_options = request.form.getlist('entity')

            if nlp != None:
                doc = nlp(lines)
                lines_rendered = displacy.render(doc, style="ent",options={"ents":cb_options})
            else:
                print("You haven't selected a model.  Select a model and then click Refresh.")

    # The View
    return render_template('revv.html', file_lines=lines_rendered, rb_option=rb_option, list_models=list_models, cb_options=cb_options, list_entities=list_entities)  #, html_lines=html_lines)

if __name__ == "__main__":
    app.run(debug = True)  #(host="0.0.0.0",port=8080)
    exit()
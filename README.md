# Revv Power Reader

Revv is a power reader that makes use of the power of Spacy module Displacy to highlight named
entities in text that can enable speed up in reading and comprehension.  It uses Flask to
deliver this as a web service.  The Revv interface is fully responsive.

Text contains a lot of stopwords and filler material that are time consuming
to go over.  By making use of this power reader, entities can be highlighted making reading
a lot easier.  

> The entities highlighted depend on the model used.  This means models trained and specialized
for specific domains can be used to highlight entities for that domain.  This makes Revv suitable
for a variety of use cases.  You can use Spacy to download compatible/specialized models.

Now, you don't have to worry about missing out on important things while reading -- Revv's
highlighted view makes sure that they are hard to miss.

## Getting started

Revv requires Spacy with at least one model and Flask.  Invoking `revv.py` starts the Flask
server on your machine at port 5000.  Open your browser on `localhost:5000` to interact with
Revv.
import os
import requests
import zipfile
import tarfile

# make needed directories 
if not os.path.isdir("../results"):
    os.mkdir("../results")

if not os.path.isdir("../assets"):
    os.mkdir("../assets")

if not os.path.exists("../assets/en_core_web_sm-3.0.0.tar.gz"):
    # installing SPACY to support NER and tagging of subject/object pairs 
    print("Downloading en_core_web_sm-3.0.0")
    response = requests.get("https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz")
    with open("../assets/en_core_web_sm-3.0.0.tar.gz", 'wb') as encore:
        encore.write(response.content)

    print("Extracting en_core_web_sm-3.0.0")
    fname = "../assets/en_core_web_sm-3.0.0.tar.gz"
    tar = tarfile.open(fname, "r:gz")
    tar.extractall(path='../assets')

if not os.path.exists("../assets/stanford-ner-4.2.0"):
    # TODO: Note, this was not able to be done automatically. Unzip manually and place in assets folder 
    print("Downloading Stanford NER 4.2.0")
    response = requests.get('https://nlp.stanford.edu/software/stanford-ner-4.2.0.zip')
    with open("../assets/stanford-ner-4.2.0.zip", 'wb') as stanford:
        stanford.write(response.content)

    print("Extracting Stanford NER 4.2.0")
    with zipfile.ZipFile("../assets/stanford-ner-4.2.0.zip", 'w') as stan:
        stan.extractall(path='../assets')

print("---------------------")
print("You have completed your setup of the enviornment.")
print("---------------------")


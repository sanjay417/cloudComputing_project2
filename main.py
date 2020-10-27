import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import storage
from google.cloud import datastore
from google.cloud import vision
from cloudStorage import bucket_upload, datastore_upload, datastore_update
CLOUD_STORAGE_BUCKET = 'cloudcomputing-project2-292023' #os.environ['CLOUD_STORAGE_BUCKET']
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list', methods=['GET', 'POST'])
def photoslist():
    datastore_client = datastore.Client()
    Kind = request.args.get('kind')
    query = datastore_client.query(kind=Kind)
    image_entities = list(query.fetch())
    #print(image_entities[0])
    return render_template('list.html', image_entities=image_entities)


@app.route('/add')
def add():
    return render_template('form.html', flag=0)


@app.route('/edit')
def edit():
    datastore_client = datastore.Client()
    blob_name = request.args.get('name')
    Kind = blob_name.split('_')
    print(Kind)
    query = datastore_client.query(kind=Kind[0])
    query.add_filter('blob_name', '=', blob_name)
    image_entities = list(query.fetch())
    print(image_entities)
    return render_template('form.html', image_entities=image_entities[0], flag=1, kind=Kind[0])


@app.route('/update', methods=['POST', 'GET'])
def update():
    kind = request.form.get('kind')
    print("kind -> ", kind)
    blob_name = request.args.get('id')
    pc = request.form.get('pc')
    print("pc -> ", pc)
    location = request.form.get('location')
    date = request.form.get('date')
    extension = blob_name.split("_")
    original_kind = extension[0]
    datastore_update(blob_name, location, date, pc, kind, original_kind, extension)
    return redirect("/")


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        print("in post")
        pc = request.form.get('pc')
        location = request.form.get('location')
        date = request.form.get('date')
        image = request.files['image']

        name = image.filename
        print("filename -> ", name)
        extension = name.split(".")
        print("Extension -> ", extension)
        upload_file_name = pc + "_" + extension[0] + "." + extension[1]
        print(upload_file_name)

        datastore_upload(location, upload_file_name, date, image, pc)
        return redirect("/")


@app.route('/delete')
def delete():
    blob_name = request.args.get('name')
    datastore_client = datastore.Client()
    Kind = blob_name.split('_')
    print(Kind)
    key = datastore_client.key(Kind[0], blob_name)
    datastore_client.delete(key)

    return redirect("/")


if __name__ == '__main__':
    app.run()


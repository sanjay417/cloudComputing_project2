from google.cloud import storage
from google.cloud import datastore
from google.cloud import vision

CLOUD_STORAGE_BUCKET = 'cloudcomputing-project2-292023'  # os.environ['CLOUD_STORAGE_BUCKET']


def bucket_upload(image, upload_file_name):
    gcs = storage.Client()
    bucket = gcs.bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(upload_file_name)

    blob.upload_from_string(
        image.read(),
        content_type=image.content_type)

    blob.make_public()
    print(blob.public_url)
    return blob


def datastore_upload(location, upload_file_name, date, image, pc):
    blob = bucket_upload(image, upload_file_name)
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = blob.public_url
    response = client.face_detection(image=image)

    response1 = client.label_detection(image=image)
    labels = response1.label_annotations
    description = []
    print('Labels:')
    for label in labels:
        print(label.description)
        description.append(label.description)
    print(description)

    if response:
        print("face exists")
        if "Mammal" in description or "Animal" in description:
            print("in animal")
            kind = "Animals"
        else:
            print("in person")
            kind = "Person"
    else:
        if "Mammal" in description or "Animal" in description:
            print("in animal")
            kind = "Animals"
        elif "Flower" in description or "Plant" in description:
            print("in flower")
            kind = "Flowers"
        else:
            print("in others")
            kind = "Others"
    datastore_client = datastore.Client()
    name = kind + "_" + blob.name
    key = datastore_client.key(kind, name)
    entity = datastore.Entity(key)
    entity["blob_name"] = name
    entity["photo_courtesy"] = pc
    entity["image_public_url"] = blob.public_url
    entity["timestamp"] = date
    entity["location"] = location
    datastore_client.put(entity)


def datastore_update(blob_name, location, date, pc, kind, original_kind, extension):
    datastore_client = datastore.Client()
    key = datastore_client.key(original_kind, blob_name)
    print("blob -> ", blob_name)
    entity = datastore_client.get(key)
    url = entity['image_public_url']
    datastore_client.delete(key)
    print("extension -> ", extension)

    blob_name = kind + "_" + pc + "_" + extension[2]
    key = datastore_client.key(kind, blob_name)
    name = kind + "_" + pc + "_" + extension[2]
    entity = datastore.Entity(key)
    entity["blob_name"] = name
    entity["photo_courtesy"] = pc
    entity["image_public_url"] = url
    entity["timestamp"] = date
    entity["location"] = location
    datastore_client.put(entity)

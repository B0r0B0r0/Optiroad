from minio import Minio
from flask import current_app
import io
import uuid

def get_minio_client():
    return Minio(
        current_app.config["MINIO_ENDPOINT"],
        access_key=current_app.config["MINIO_ACCESS_KEY"],
        secret_key=current_app.config["MINIO_SECRET_KEY"],
        secure=False
    )

def upload_file(file_storage):
    client = get_minio_client()
    bucket = current_app.config["MINIO_BUCKET"]

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    file_bytes = file_storage.read()
    filename = f"{uuid.uuid4()}.{file_storage.filename.rsplit('.', 1)[-1]}"

    client.put_object(
        bucket,
        filename,
        io.BytesIO(file_bytes),
        len(file_bytes),
        content_type=file_storage.mimetype
    )

    return f"/{bucket}/{filename}"

def send_file(filename):
    client = get_minio_client()
    bucket = current_app.config["MINIO_BUCKET"]

    try:
        response = client.get_object(bucket, filename)
        return response
    except Exception as e:
        print(f"Error retrieving file: {e}")
        return None
    
def delete_file(filename):
    client = get_minio_client()
    bucket = current_app.config["MINIO_BUCKET"]
    to_delete = filename.split("/")[-1]  
    try:
        client.remove_object(bucket, to_delete)
        return True
    except Exception as e:
        return False
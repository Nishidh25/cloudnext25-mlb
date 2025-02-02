from google.cloud import storage
import os
import tempfile

# Initialize the Google Cloud Storage client
storage_client = storage.Client()

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):

    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob (file) in the bucket
    blob = bucket.blob(destination_blob_name)

    # Upload the file to GCS
    blob.upload_from_filename(source_file_path)

    print(f"File {source_file_path} uploaded to {destination_blob_name}.")
    
    gs_url = f"gs://{bucket_name}/{destination_blob_name}"
    return gs_url, destination_blob_name #blob.public_url

def download_from_gcs(bucket_name, source_blob_name, destination_file_path):
    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)

    # Get the blob (file) from the bucket
    blob = bucket.blob(source_blob_name)

    # Download the file to the local system
    blob.download_to_filename(destination_file_path)

    print(f"File {source_blob_name} downloaded to {destination_file_path}.")



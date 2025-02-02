from google.cloud import storage

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    
    # Initialize the Google Cloud Storage client
    storage_client = storage.Client.from_service_account_json('./ss-genai-npd-svc-prj-01-8ccca879e424.json')
    storage_client = storage.Client()

    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob (file) in the bucket
    blob = bucket.blob(destination_blob_name)

    # Upload the file to GCS
    blob.upload_from_filename(source_file_path)

    print(f"File {source_file_path} uploaded to {destination_blob_name}.")
    
    gs_url = f"gs://{bucket_name}/{destination_blob_name}"
    return gs_url #blob.public_url

# Example usage
bucket_name = "your-bucket-name"  # Replace with your GCS bucket name
source_file_path = "path/to/your/local/file.txt"  # Replace with the local file path
destination_blob_name = "destination/path/in/bucket/file.txt"  # The name/path you want the file to have in GCS

upload_to_gcs(bucket_name, source_file_path, destination_blob_name)


# Path to your service account JSON key file
key_path = './ss-genai-npd-svc-prj-01-8ccca879e424.json'  


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./ss-genai-npd-svc-prj-01-8ccca879e424.json"


# Create credentials object from the service account
credentials = service_account.Credentials.from_service_account_file(key_path)


# Helper functions to process images 
# ## convert_image_to_jpg
def convert_image_to_jpg(image_path):
    try:

        # Open the image file
        with Image.open(image_path) as img:
            # Convert and save the image as JPG
            with io.BytesIO() as output:
                img.save(output, format='JPEG')
                return output.getvalue()
                
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# ## Image encoding to Base64
def image_encode(image_path):
    # Get the image data as a JPG
    img_data = convert_image_to_jpg(image_path)
    
    if img_data:
        # Convert the image data to Base64 encoding
        return base64.b64encode(img_data).decode("utf-8")
    else:
        return None



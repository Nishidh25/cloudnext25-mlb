from PIL import Image
import base64
import requests
import io


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


def download_image(image_url, destination_path):
    # Send a GET request to the image URL
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open the destination file in binary write mode and save the content
        with open(destination_path, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully downloaded to {destination_path}")
        return destination_path
    else:
        print(f"Failed to retrieve the image. HTTP Status code: {response.status_code}")

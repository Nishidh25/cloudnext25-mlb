import os
import requests
from PIL import Image as pilimage
from io import BytesIO
from datetime import datetime
import os


LOCATION = "us-central1"  # @param {type:"string"}

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "./vertex_ai_service_account.json"

import vertexai
vertexai.init(os.getenv("project_id",'mlb-hackathon-448812'), location=LOCATION)

from vertexai.preview.vision_models import (
    Image,
    ImageGenerationModel,
    SubjectReferenceImage,
)


generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
customization_model = ImageGenerationModel.from_pretrained("imagen-3.0-capability-001")





def load_image_from_url(url: str, save_path: str = "./load_from_url"+datetime.now().strftime("%Y%m%d_%H%M%S")+".jpg"):
    # Send a GET request to fetch the image from the URL
    response = requests.get(url)
    
    if response.status_code == 200:
        # Open the image using PIL from the bytes response
        img = pilimage.open(BytesIO(response.content))
        
        # Save the image to the specified path
        img.save(save_path)
        
        return Image.load_from_file(save_path)
    else:
        print(f"Failed to fetch image from URL. Status code: {response.status_code}")
        return None

def generate_from_imagen(url:str,style:str,type = 'person'): # Type can be person or logo 

    subject_image_1  = load_image_from_url(url)

    if type == 'person':
        subject_reference_image_1 = SubjectReferenceImage(
            reference_id=1,
            image=subject_image_1,
            subject_description="Picture of a person",
            subject_type='person',
        )
    else:
        subject_reference_image_1 = SubjectReferenceImage(
            reference_id=1,
            image=subject_image_1,
            subject_description="Picture of a team logo",
            subject_type='default',
        )

    prompt = f"Generate an {style} style image of [1]"

    image = customization_model._generate_images(
        prompt=prompt,
        number_of_images=2,
        aspect_ratio="3:4",
        reference_images=[subject_reference_image_1],
        safety_filter_level="block_few",
        person_generation="allow_adult",
    )
    save_path = "./generated_image_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png"
    try:
        image[0].save(save_path)
    except:
        print("Error while generating images")
    return save_path
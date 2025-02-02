## Working Video/Screenshots





# Showcasing the journey to build this project. Thoughts, challenges and solutions 



## Selecting the topic/ challenge

Challenge 2: Personalized Fan Highlights: Build a system that allows fans to select team(s), player(s), etc. to follow and create audio, video, and/or text digests that fans could receive on a regular cadence to stay up on the latest highlights and commentary. Ensure your solution supports fans who speak English, Spanish, and Japanese. 

### Understanding user journeys


### Understanding the Data
    Understanding the API's: used Google's Notebook LM to understand the API's and How to use them

### Brainstorming a solution:
    Needs to be a web app so that it is not any platform limiting, and can be prototyped quickly
    Using Gemini to create Personalised digests from player highlights, and is multi lingual
    Using VEO to create GIF's from Picture Highlights
    Using Imagen to create some Images
    Gradio will be used for Frontend Development , is desktop and mobile friendly. Low code solution in python
    User info to be stored in Cloud SQL and all other OBJECTS(Images, videos) to be stored in BigQuery
    


## Designing the Google Cloud Architecture (Selecting "right" Tools, Methodology)
The whole point is to design reliable and scalable solution
 
![Solution Architecture](/images/cloud_architecture.png)

Microservice Architecture 
Service 1: Frontend for the MLB (using Gradio for Quick development in python). Audio/Text based inputs as well
Service 2: Generating Personalized Highlights using Vertex AI Models (Gemini, VEO, Imagen), which is used to generate highlights based on the users preference 
Service 3: Send personalized digests via email to users (using Gmail API)

Google Cloud:
Compute - Cloud Run
Network - Google VPC
Storage - GCS (for images/gifs)
Storage - Cloud SQL (User Metadata)


## Explanation of modules/services





## How to deploy/run on your environment




## 



## Judging Criteria Checklist 

Technical Implementation (40%):
Does the Submission demonstrate a strong understanding and effective use of relevant Google Cloud services? 
Microservice Architecture: 

Does it effectively integrate and utilize relevant MLB™ data sources? See more in the rules


Demo and Video presentation (30%):
Is the Submission presented in a clear, concise, and engaging manner? 
Does the presentation effectively showcase the technical challenges and solutions implemented in the Submission? See more in the rules


Innovative Build (20%):
Does the Submission leverage the latest Google Cloud AI and ML technologies, including those launched since Google Cloud Next 2024? (e.g., Imagen, new Vertex AI or AI Studio features). See more in the rules

Creative Idea (10%):
Does the Submission creatively address the specific challenge for MLB™? Does the Submission introduce a truly novel concept or approach to enhance the baseball fan experience? See more in the rules

# My MLB: Fan Personalized Highlights for MLB

Google Cloud x MLB Hackathon Submission:

Challenge 2: Personalized Fan Highlights: Build a system that allows fans to select team(s), player(s), etc. to follow and create audio, video, and/or text digests that fans could receive on a regular cadence to stay up on the latest highlights and commentary. Ensure your solution supports fans who speak English, Spanish, and Japanese. 

#### Inspiration
The main inspiration behind this project is to bring fans closer to the game than ever before, creating an experience where every fan feels like the Highlight is specifically tailored to them.

#### What it does
This is a web-based solution designed for MLB fans, allowing them to subscribe to teams and players. Based on their personas and preferred languages, they will receive personalized digests that keep them updated on everything they care about.


Get basic details about the team/player in your language and persona

<img src="/images/home_light_theme.png" width="400"/>                             <img src="/images/home_light_theme_japanese.png" width="400"/> 

Sends personalised Email digests/highlights to users of latest game using Gemini 2.0 and Gmail API

<img src="/images/gmail-team_digest_english.png" width="400"/>                    <img src="/images/gmail-team_digest_spanish.png" width="400"/>

Ask about any MLB Rule uisng Vertex AI Agent Builder:

<img src="/images/vertexsearch_mlb_rules.png" width="400"/> 


## Brainstorming a Solution

- **Web App**: Needs to be a web app so that it is not platform-limiting and can be prototyped quickly.
- **Gemini**: Used to create personalized digests from player highlights and supports multiple languages.
- **VEO**: Used to create GIFs from picture highlights.
- **Imagen**: Used to generate images from highlights.
- **Gradio**: Will be used for frontend development. It is a low-code solution in Python, mobile and desktop-friendly.
- **User Info Storage**: User information will be stored in Cloud SQL.
- **Media Storage**: All other objects (images, videos) will be stored in BigQuery.



---
## Designing the Google Cloud Architecture

Selecting "right" Tools, Methodology. The whole point is to design reliable and scalable solution

Solution Architecture: 

<img src="/images/cloud_architecture.png" alt="Solution Architecture" width="70%" />

### Google Cloud Services Used

| Product Name             | Description                                                   | Category             |
|--------------------------|---------------------------------------------------------------|----------------------|
| Cloud Run Service        | Fully managed application platform, serverless compute       | Serverless Compute          |
| Cloud Run Functions      | Event-driven serverless functions, triggered by Pub/Sub or HTTP | Serverless Compute          |
| Cloud Build              | Build and tag containerized application on Google Cloud | Serverless Compute          |
| Vertex AI                | One AI platform offering a wide range of ML tools for developers | AI |
| Agent Builder            | No-code tool for building AI agents and chatbots             | AI                   |
| Cloud SQL                | Fully managed relational database for MySQL, PostgreSQL, and SQL Server | Databases            |
| Cloud Storage            | Scalable object storage for images, videos, and other large files | Storage             |
| Artifact Registery       | Store Cloud Run Images before deployment | Storage             |
| Google OAuth 2.0         | Secure authentication with single sign-on (SSO) capabilities | Security             |
| Secret Manager           | Secure storage for managing API keys, credentials, and other sensitive data | Security             |
| Serverless VPC           | Connect to private resources in Google Cloud without the need for traditional network management | Network              |
| Cloud Armor              | Security service offering DDoS protection and ML-based threat mitigation | Security             |

---

### Microservice Architecture

The architecture used 3 services, for detail about each service click on their link

- **[Service 1: Frontend Service](./frontend-service/)**: Frontend for the MLB (using Gradio for quick development in Python). Audio/Text-based inputs as well.
- **[Service 2: Gen AI Service](./genai-service/)**: Generating Personalized Highlights using Vertex AI Models (Gemini, VEO, Imagen), which is used to generate highlights based on the user's preference.
- **[Service 3 Gmail Service](./email-service/)**: Send personalized digests via email to users (using Gmail API).


## How to deploy/run on your environment

1. Configure Google Cloud Project.
2. Configure and Enable Required API's
3. Setup Cloud SQL Instance
4. Setup Serverless VPC
5. Enable Secret Manager and update deploy.sh with your environment secret values
6. deploy.sh which will deploy all the 3 individual servicesat once

```sh deploy.sh```

Building a Teraform script for deployment is still pending due to time constraints of the Hackathon





FROM python:3.9-slim

WORKDIR /usr/src/app
COPY . .
RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential
RUN apt-get install -y ffmpeg
RUN pip install -r requirements.txt

CMD ["fastapi", "run", "main.py","--port", "8080"]
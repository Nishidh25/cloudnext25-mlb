FROM python:3.12-slim

WORKDIR /usr/src/app
COPY . .
RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential
RUN pip install -r requirements.txt
EXPOSE 8080
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV PYTHONUNBUFFERED=1
CMD ["fastapi", "run", "main.py","--port", "8080"]
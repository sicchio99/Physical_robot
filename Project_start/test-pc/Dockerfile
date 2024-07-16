FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgl1-mesa-glx

WORKDIR /app
COPY . .
CMD ["python", "test-pc.py"]
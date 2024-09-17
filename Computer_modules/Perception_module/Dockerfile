FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgl1-mesa-glx

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "perception.py"]
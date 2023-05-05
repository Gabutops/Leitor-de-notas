FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update -y

# Install Tkinter
RUN apt-get install tk -y
COPY . .

CMD [ "python", "app.py" ]

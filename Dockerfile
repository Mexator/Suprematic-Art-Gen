FROM python:3.8

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY *.py /app
COPY launch.sh /app
COPY input /app/input

CMD [ "bash", "launch.sh" ]

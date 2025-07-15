FROM python:3.9

COPY . /home
WORKDIR /home

RUN pip3 install -r requirements.txt

EXPOSE $PORT

CMD uvicorn app:app --host 0.0.0.0 --port $PORT

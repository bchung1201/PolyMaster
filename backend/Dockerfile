FROM python:3.9

COPY . /home
WORKDIR /home

RUN pip3 install -r requirements.txt

# Download spaCy model after installing spaCy
RUN python -m spacy download en_core_web_sm

EXPOSE $PORT

CMD uvicorn app:app --host 0.0.0.0 --port $PORT

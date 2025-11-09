FROM python:3.12

ENV HOME /root
WORKDIR /root

COPY ./requirements.txt ./requirements.txt
COPY ./server.py ./server.py

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD python3 -u server.py
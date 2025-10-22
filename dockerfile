FROM python:3.12

COPY slopserver/ requirements.txt /slopserver/
WORKDIR /slopserver/

RUN python3 -m pip install -r requirements.txt
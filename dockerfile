FROM python:3.12

COPY slopserver/ requirements.txt /slopserver/
WORKDIR /slopserver/

RUN python3 -m pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT [ "fastapi", "run", "--workers", "4", "/slopserver/server.py" ]
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slopserver.server import app as slopserver_app

client = TestClient(slopserver_app)
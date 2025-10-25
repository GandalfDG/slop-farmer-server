"""API Operations

- signup
- verify email
- Get auth token
- get top x reported domains
- get reports for given domains/pages
- post report
"""
from typing import Annotated
from datetime import datetime, timedelta

import uvicorn

from fastapi import Body, Depends, FastAPI, Form, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic import AfterValidator, Base64Str
from pydantic_settings import BaseSettings

from sqlalchemy import create_engine

from pwdlib import PasswordHash

from altcha import ChallengeOptions, create_challenge

import jwt

from uuid import uuid4


from slopserver.models import Domain, Path, User
from slopserver.models import SlopReport, SignupForm, altcha_validator
from slopserver.db import select_slop, insert_slop, get_user, create_user
from slopserver.common import TEMP_HMAC_KEY

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ServerSettings(BaseSettings):
    db_url: str = "postgresql+psycopg://slop-farmer@192.168.1.163/slop-farmer"
    token_secret: str = "5bcc778a96b090c3ac1d587bb694a060eaf7bdb5832365f91d5078faf1fff210"
    # altcha_secret: str

settings = ServerSettings()


DB_ENGINE = create_engine(settings.db_url)
TOKEN_SECRET = settings.token_secret
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

TEMP_ORIGINS = [
    "*"
]

app.add_middleware(CORSMiddleware, allow_origins=TEMP_ORIGINS,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)

password_hash = PasswordHash.recommended()


def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(clear_password, hashed_password):
    return password_hash.verify(clear_password, hashed_password)

def auth_user(email: str, password: str, db_engine):
    # TODO Salt
    user: User = get_user(email, db_engine)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def generate_auth_token(username):
    expiration = datetime.now() + timedelta(days=30)
    uuid = username
    bearer_token = {
        "iss": "slopserver",
        "exp": int(expiration.timestamp()),
        "aud": "slopserver",
        "sub": str(uuid),
        "client_id": str(uuid),
        "iat": int(datetime.now().timestamp()),
        "jti": str(uuid)
    }

    encoded_jwt = jwt.encode(bearer_token, TOKEN_SECRET, ALGO)   
    return encoded_jwt

def verify_auth_token(token: str):
    try:
        token = jwt.decode(token, TOKEN_SECRET, ALGO, audience="slopserver")
    except:
        raise HTTPException(status_code=401, detail="invalid access token")

@app.post("/report")
async def report_slop(report: SlopReport, bearer: Annotated[str, AfterValidator(verify_auth_token), Header()]):
    insert_slop(report.slop_urls, DB_ENGINE)

@app.post("/check")
async def check_slop(check: Annotated[SlopReport, Body()], bearer: Annotated[str, AfterValidator(verify_auth_token), Header()]):
    slop_results = select_slop(check.slop_urls, DB_ENGINE)
    return slop_results

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    pass

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username, DB_ENGINE)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.post("/signup")
async def signup_form(form_data: Annotated[SignupForm, Form()]):
    # if we're here, form is validated including the altcha
    # check for existing user with the given email
    if get_user(form_data.email, DB_ENGINE):
        # user already exists
        raise HTTPException(status_code=409, detail="User already exists")

    # create user
    create_user(form_data.email, get_password_hash(form_data.password), DB_ENGINE)

@app.get("/altcha-challenge")
async def altcha_challenge():
    options = ChallengeOptions(
        expires=datetime.now() + timedelta(minutes=10),
        max_number=100000,
        hmac_key=TEMP_HMAC_KEY
    )
    challenge = create_challenge(options)
    return challenge

@app.post("/login")
async def simple_login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    user = auth_user(username, password, DB_ENGINE)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = generate_auth_token(username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/altcha-challenge")
async def altcha_verify(payload: Annotated[Base64Str, AfterValidator(altcha_validator)]):
    # if verified, return a JWT for anonymous API access
    expiration = datetime.now() + timedelta(days=30)
    uuid = uuid4()
    bearer_token = {
        "iss": "slopserver",
        "exp": int(expiration.timestamp()),
        "aud": "slopserver",
        "sub": str(uuid),
        "client_id": str(uuid),
        "iat": int(datetime.now().timestamp()),
        "jti": str(uuid)
    }

    encoded_jwt = jwt.encode(bearer_token, TOKEN_SECRET, ALGO)

    return encoded_jwt
    
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
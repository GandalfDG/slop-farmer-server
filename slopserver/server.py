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
from fastapi.responses import HTMLResponse

from pydantic import AfterValidator, Base64Str


from sqlalchemy import create_engine

from pwdlib import PasswordHash

from altcha import ChallengeOptions, create_challenge

import jwt

from uuid import uuid4

from slopserver.settings import settings
from slopserver.models import Domain, Path, User
from slopserver.models import SlopReport, SignupForm, altcha_validator
from slopserver.db import select_slop, insert_slop, get_user, create_user, verify_user_email

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

def generate_verification_token(username):
    expiration = datetime.now() + timedelta(days=2)
    verification_token = {
        "iss": "slopserver",
        "exp": int(expiration.timestamp()),
        "sub": username
    }

    encoded_jwt = jwt.encode(verification_token, TOKEN_SECRET, ALGO)
    return encoded_jwt

def get_token_user(decoded_token):
    user = get_user(decoded_token["sub"], DB_ENGINE)
    return user

def verify_auth_token(token: str):
    try:
        token = jwt.decode(token, TOKEN_SECRET, ALGO, audience="slopserver")
        return token
    except:
        raise HTTPException(status_code=401, detail="invalid access token")

def verify_verification_token(token: str):
    try:
        token = jwt.decode(token, TOKEN_SECRET, ALGO)
        return token
    except:
        raise HTTPException(status_code=404, detail="invalid verification URL")

@app.post("/report")
def report_slop(report: SlopReport, bearer: Annotated[str, AfterValidator(verify_auth_token), Header()]):
    user = get_token_user(bearer)
    insert_slop(report.slop_urls, DB_ENGINE, user)

@app.post("/check")
def check_slop(check: Annotated[SlopReport, Body()], bearer: Annotated[str, AfterValidator(verify_auth_token), Header()]):
    slop_results = select_slop(check.slop_urls, DB_ENGINE)
    return slop_results

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    pass

@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username, DB_ENGINE)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.post("/signup")
def signup_form(form_data: Annotated[SignupForm, Form()]):
    # if we're here, form is validated including the altcha
    # check for existing user with the given email
    if get_user(form_data.email, DB_ENGINE):
        # user already exists
        raise HTTPException(status_code=409, detail="User already exists")

    # create user
    create_user(form_data.email, get_password_hash(form_data.password.get_secret_value()), DB_ENGINE)

    # send verification email
    # create a jwt encoding the username and a time limit to be the verification URL
    token = generate_verification_token(form_data.email)
    return token



@app.get("/verify")
def verify_email(token: Annotated[str, AfterValidator(verify_verification_token)]):
    user = get_user(token["sub"], DB_ENGINE)
    if not user:
        raise HTTPException(status_code=404, detail="invalid verification URL")
    if user.email_verified:
        raise HTTPException(status_code=404, detail="already verified")
    
    verify_user_email(user, DB_ENGINE)
    html = f"""
    <html>
        <head>
        </head>
        <body>
            <p>{token["sub"]} verified. You may log in now.</p>
        </body>
    </html>
    """

    return HTMLResponse(content=html, status_code=200)


@app.get("/altcha-challenge")
def altcha_challenge():
    options = ChallengeOptions(
        expires=datetime.now() + timedelta(minutes=10),
        max_number=80000,
        hmac_key=settings.altcha_secret
    )
    challenge = create_challenge(options)
    return challenge

@app.post("/login")
def simple_login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    user = auth_user(username, password, DB_ENGINE)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = generate_auth_token(username)
    return {"access_token": token, "token_type": "bearer"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
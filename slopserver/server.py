"""API Operations

- signup
- verify email
- Get auth token
- get top x reported domains
- get reports for given domains/pages
- post report
"""
from typing import Annotated
import uvicorn

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import create_engine

from pwdlib import PasswordHash

from slopserver.models import Domain, Path, User
from slopserver.models import SlopReport
from slopserver.db import select_slop, insert_slop, get_user

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

TEMP_ENGINE = create_engine("postgresql+psycopg://slop-farmer@192.168.1.163/slop-farmer")
TEMP_SECRET = "5bcc778a96b090c3ac1d587bb694a060eaf7bdb5832365f91d5078faf1fff210"
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

@app.post("/report")
async def report_slop(report: SlopReport):
    insert_slop(report.slop_urls, TEMP_ENGINE)

@app.post("/check")
async def check_slop(check: SlopReport):
    slop_results = select_slop(check.slop_urls, TEMP_ENGINE)
    return slop_results

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    pass

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username, TEMP_ENGINE)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
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

from slopserver.models import Domain, Path, User
from slopserver.models import SlopReport
from slopserver.db import select_slop, insert_slop, get_user

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

temp_engine = create_engine("postgresql+psycopg://slop-farmer@192.168.1.163/slop-farmer")

@app.post("/report")
async def report_slop(report: SlopReport):
    insert_slop(report.slop_urls, temp_engine)

@app.post("/check")
async def check_slop(check: SlopReport):
    slop_results = select_slop(check.slop_urls, temp_engine)
    return slop_results

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    pass

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username, temp_engine)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
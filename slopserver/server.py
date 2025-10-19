"""API Operations

- signup
- verify email
- Get auth token
- get top x reported domains
- get reports for given domains/pages
- post report
"""
import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine
from slopserver.models import Domain, Path, User
from slopserver.models import SlopReport
from slopserver.db import select_slop, insert_slop

app = FastAPI()

temp_engine = create_engine("postgresql+psycopg://slop-farmer@192.168.1.163/slop-farmer")

@app.post("/report/")
async def report_slop(report: SlopReport):
    insert_slop(report.slop_urls, temp_engine)

@app.post("/check/")
async def check_slop(check: SlopReport):
    slop_results = select_slop(check.slop_urls, temp_engine)
    return slop_results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
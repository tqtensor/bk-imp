import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import HTTPBearer
from jobs.api import api_router

load_dotenv()

http_bearer = HTTPBearer()

app = FastAPI(
    title="Customer Churn Prevention",
)


async def verify_token(api_token: Annotated[str, Header()]):
    if api_token != os.getenv("API_TOKEN"):
        raise HTTPException(status_code=400, detail="API Token header invalid")


app.include_router(
    router=api_router,
    dependencies=[Depends(verify_token)],
)

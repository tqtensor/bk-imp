import logging

from fastapi import FastAPI
from jobs.api import api_router


# Define the filter
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.args
            and len(record.args) >= 3
            and record.args[2] != "/healthcheck"
        )


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

app = FastAPI(
    title="Customer Churn Prevention",
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(
    router=api_router,
)

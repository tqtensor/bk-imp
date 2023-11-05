from fastapi import APIRouter
from jobs.inference import router as inference_router
from jobs.optimization import router as optimization_router

api_router = APIRouter()
api_router.include_router(optimization_router, tags=["Optimization"])
api_router.include_router(inference_router, tags=["Inferences"])

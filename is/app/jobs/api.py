from fastapi import APIRouter
from jobs.dataset import router as dataset_router
from jobs.model import router as model_router
from jobs.optimization import router as optimization_router

api_router = APIRouter()
api_router.include_router(dataset_router, tags=["Datasets"])
api_router.include_router(model_router, tags=["Models"])
api_router.include_router(optimization_router, tags=["Optimizations"])

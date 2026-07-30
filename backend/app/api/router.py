from fastapi import APIRouter
from app.api.endpoints import (
    generate,
    llm_endpoint,
    requirements_endpoint,
    architecture_endpoint,
    database_endpoint,
    documentation_endpoint,
    scaffold_endpoint,
    export_endpoint,
)

api_router = APIRouter()
api_router.include_router(generate.router, tags=["generator"])
api_router.include_router(llm_endpoint.router, prefix="/test", tags=["llm"])
api_router.include_router(requirements_endpoint.router, tags=["agents"])
api_router.include_router(architecture_endpoint.router, tags=["architecture"])
api_router.include_router(database_endpoint.router, tags=["database"])
api_router.include_router(documentation_endpoint.router, tags=["documentation"])
api_router.include_router(scaffold_endpoint.router, tags=["scaffold"])
api_router.include_router(export_endpoint.router, tags=["export"])

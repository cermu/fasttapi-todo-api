import fastapi
from fastapi import status
from .schemas import SystemHealthCheckBase
from .service import SystemHealthCheckervice

system_health_router = fastapi.APIRouter(prefix="/healthchecks")


@system_health_router.get("/", response_model=SystemHealthCheckBase, status_code=status.HTTP_200_OK)
async def check_application_status():
    return await SystemHealthCheckervice().check_system_health()


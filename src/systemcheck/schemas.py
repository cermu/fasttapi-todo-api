from pydantic import BaseModel


class SystemHealthCheckBase(BaseModel):
    ping: str
    message: str
    is_application_healthy: bool

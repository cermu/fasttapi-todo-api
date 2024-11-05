from pydantic import BaseModel


class SystemHealthCheckBase(BaseModel):
    ping: str
    message: str
    status: str

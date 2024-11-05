from .schemas import SystemHealthCheckBase


class SystemHealthCheckervice:
    """
    This class provides a method to check the health of the application
    """
    async def check_system_health(self):
        """
        Check the applications status

        Returns:
            results: SystemHealthCheckBase
        """
        results = SystemHealthCheckBase(
            ping="pong", 
            message="the application is up and running", 
            is_application_healthy=True,
        )
        return results
        

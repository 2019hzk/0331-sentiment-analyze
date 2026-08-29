from typing import Annotated

from fastapi import Depends

from atguigu.app.services.system_service import SystemService


def get_system_service():
    return SystemService()


SystemServiceDep = Annotated[SystemService, Depends(get_system_service)]

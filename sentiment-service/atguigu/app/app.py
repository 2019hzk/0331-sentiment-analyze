from fastapi import FastAPI

from atguigu.app.routers.rest import system_router
from atguigu.app.exceptions.exception_handlers import register_exception_handlers

app = FastAPI(description="舆情项目")

register_exception_handlers(app)

app.include_router(system_router.router)

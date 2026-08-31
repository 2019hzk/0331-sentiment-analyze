"""

职责：
1. 管理研究任务对象
2. 管理其它的异步任务
"""
import asyncio
import uuid
from collections.abc import Coroutine
from dataclasses import dataclass


@dataclass(slots=True)
class ResearchTaskInfo:
    query: str
    task_id: str


class TaskManager:
    def __init__(self):
        # 存储研究任务（业务用的）
        self.research_tasks: dict[str, ResearchTaskInfo] = {}
        # 存储异步任务 (通用)
        self.async_tasks: set[asyncio.Task] = set()

    def create_research_task(self, query: str) -> ResearchTaskInfo:
        # 1. 创建研究任务
        research_task = ResearchTaskInfo(query=query, task_id=str(uuid.uuid4().hex))

        # 2. 存储研究任务
        self.research_tasks[research_task.task_id] = research_task

        # 3. 返回研究任务对象

        return research_task

    def get_research_task(self, task_id: str) -> ResearchTaskInfo:
        return self.research_tasks[task_id]

    def submit_task(self, coro: Coroutine):
        # 1. 创建异步任务(协程对象)----->一个事件循环线程并发执行两个协程任务
        task = asyncio.create_task(coro)
        # 2. 存储异步任务
        self.async_tasks.add(task)

        # 3. 异步任务做完之后 从容器中移除
        task.add_done_callback(self.async_tasks.discard)

    async def cancel_tasks(self):
        """
        职责：取消未做完的后台任务
        :return:
        """

        # 1. 收集未做完的任务
        undone_tasks = tuple(task for task in self.async_tasks if not task.done())

        # 2. 取消
        for undone_task in undone_tasks:
            undone_task.cancel()  # 发送取消任务的信号

        if undone_tasks:
            await  asyncio.gather(*undone_tasks,return_exceptions=True)


task_manager = TaskManager()

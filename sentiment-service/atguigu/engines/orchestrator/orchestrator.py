from collections.abc import Callable
from typing import Awaitable

from atguigu.engines.common.llm import LLMClient
from atguigu.engines.common.logger import router_by_role_log
from atguigu.engines.common.research_graph_runtime import ProgressCallback, ProgressUpdate
from atguigu.engines.contract.agent_role import AgentInfoRoleKey
from atguigu.engines.contract.events import publish_role_progress, RoleProgressEvent, publish_role_error, \
    RoleErrorEvent, RoleResultEvent, publish_role_result
from atguigu.engines.insight_agent.agent import insight_agent_invoker
from atguigu.engines.media_agent.agent import media_agent_invoker
from atguigu.engines.common.task_manager import task_manager
from atguigu.engines.common.report import get_report_dir
from loguru import logger

AGENT_INVOKER = Callable[[AgentInfoRoleKey, str, str, LLMClient, str, ProgressCallback], Awaitable[None]]


class OrchestratorResearchAgent:

    def __init__(self):
        self.agent_invoker: dict[AgentInfoRoleKey, AGENT_INVOKER] = {
            "insight": insight_agent_invoker,
            "media": media_agent_invoker
        }

    def dispatch_task(self,
                      task_id: str,
                      query: str):
        """
        将研究任务转发给研究角色的Agent处理.
        启动两个角色Agent执行的异步任务
        :param task_id:
        :param query:
        :return:
        """

        for agent_role in self.agent_invoker.keys():
            task_manager.submit_task(self.execute_research_task(task_id, query, agent_role))

    async def execute_research_task(self, task_id: str, query: str, role: AgentInfoRoleKey):
        with router_by_role_log(role):
            self._publish_progress(
                task_id,
                role,
                ProgressUpdate(status="starting", message="开始执行研究", progress_pct=0)
            )

            # 1. 获取两个角色的llm客户端
            llm_client = LLMClient.from_role(role)

            # 2. 得到md文档的目录
            output_dir = get_report_dir(task_id, role)

            # 3. 执行两个角色的agent
            try:
                await self.agent_invoker[role](
                    role,
                    task_id,
                    query,
                    llm_client,
                    output_dir,
                    lambda update: self._publish_progress(task_id, role, update)
                )

            except Exception as exec:
                logger.error(f"{role} 研究智能体执行期间出现了异常: {exec}")
                publish_role_error(
                    RoleErrorEvent(task_id=task_id, role=role, error=str(exec))
                )
                return
            publish_role_result(RoleResultEvent(task_id=task_id, role=role))

    @staticmethod
    def _publish_progress(
            task_id: str, role: AgentInfoRoleKey, update: ProgressUpdate
    ) -> None:
        """发布指定研究角色的进度事件。"""
        publish_role_progress(
            RoleProgressEvent(
                task_id=task_id,
                role=role,
                status=update.status,
                message=update.message,
                progress_pct=update.progress_pct
            )
        )




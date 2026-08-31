from atguigu.engines.orchestrator.orchestrator import OrchestratorResearchAgent
from atguigu.engines.common.task_manager import task_manager


class ResearchService:
    def __init__(self):
        self.orchestrator = OrchestratorResearchAgent()

    def research(self, query: str) -> str:
        """
        职责：开始进行舆论话题的研究
        :param query:
        :return:
        task_id:研究任务ID
        """
        # 1. 创建研究任务
        research_task = task_manager.create_research_task(query)

        # 2. 利用协调者将研究任务转发走
        self.orchestrator.dispatch_task(research_task.task_id, query)

        # 3. 将研究任务的任务ID返回
        return research_task.task_id

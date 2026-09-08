from typing import Any
from atguigu.engines.common.research_graph_runtime import ResearchNode
from atguigu.engines.insight_agent.state import InsightState
from atguigu.engines.contract.agent_role import display_agent_name
from atguigu.engines.insight_agent.tools.retrival_service import RetrivalService


class EvidenceRetrievalNode(ResearchNode):
    """调用私域召回服务获取尚未合并的原始证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """执行私域召回并返回尚未合并的原始命中记录"""
        agent_name = display_agent_name(self.context.role)
        self.context.report_progress("searching", f"{agent_name} 开始执行私域信息搜索", 10)
        evidence_records = await RetrivalService().retrival_evidence(self.context.query)
        self.context.report_progress("searching", f"{agent_name} 执行私域信息搜索完成", 20)
        return {"retrieved_records": evidence_records}

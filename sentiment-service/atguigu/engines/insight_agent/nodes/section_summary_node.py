from typing import Any

from atguigu.engines.common.section_summary import BaseSectionSummaryNode
from atguigu.engines.prompts.insight import INSIGHT_SECTION_SUMMARY_SYSTEM_PROMPT


class SectionSummaryNode(BaseSectionSummaryNode):
    """私域章节摘要节点:基于证据包生成各章节正文"""
    system_prompt = INSIGHT_SECTION_SUMMARY_SYSTEM_PROMPT
    fallback_body = "该章节未有相关内容，本章节暂不做任何延伸"
    def _retrieval_text(self, state: dict[str, Any], cursor: int) -> str:
        """章节证据对应的检索文本，默认取研究主题"""
        return self.context.query

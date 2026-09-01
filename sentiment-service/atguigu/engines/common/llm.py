import asyncio
from typing import TypeVar, Any

from pydantic import BaseModel

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from atguigu.engines.common.retries import with_retry
from atguigu.engines.contract.agent_role import AgentInfoRoleKey, AGENT_ROLE_INFOS
from atguigu.engines.contract.settings import get_settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    定义LLM客户端以及模型调用方式
    """

    def __init__(self,
                 model_name: str,
                 model_provider: str,
                 api_key: str,
                 base_url: str
                 ):
        self.model_name = model_name
        self.model_provider = model_provider
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_role(cls, role: AgentInfoRoleKey) -> "LLMClient":
        """
        职责： 根据不同角色获取到对应的模型提供商客户端
        :param role:
        :return:
        """

        # 1. 获取配置信息
        settings = get_settings()

        # 2. 获取Agent的配置信息前缀
        config_prefix = AGENT_ROLE_INFOS[role].config_prefix

        # 3. 创建LLMClient
        return cls(
            model_name=getattr(settings, f"{config_prefix}_MODEL_NAME"),
            model_provider=getattr(settings, f"{config_prefix}_MODEL_PROVIDER"),
            api_key=getattr(settings, f"{config_prefix}_API_KEY"),
            base_url=getattr(settings, f"{config_prefix}_BASE_URL")
        )

    @with_retry
    async def generate_text(self,
                            system_prompt: str,
                            user_prompt: str
                            ) -> str:
        """
        目标方法
        职责：调用LLMClient返回文本内容
        同步 or 异步（选择）
        流式（选择） or 非流式
        原因：用流式的方式实现非流式效果（长文本的超时连接更加的安全）

        :param system_prompt:
        :param user_prompt:
        :return:
        """

        # 1. 构建消息内容
        message_context = self._build_message_context(system_prompt, user_prompt)

        # 2. 定义模型实例
        chat_model = self.init_model_object()

        # 3. 调用模型
        final_chunks = []
        try:
            async for chunk in chat_model.astream(message_context):
                # 海象运算符
                if text := chunk.text:
                    final_chunks.append(text)
        except Exception as exec:
            raise ValueError(f"{self.model_name}调用失败，原因:{str(exec)}")

        return "".join(final_chunks)

    @with_retry
    async def generate_object(self,
                              system_prompt: str,
                              user_prompt: str,
                              structed_object: type[T]
                              ) -> T:
        """
        职责：调用LLMClient返回结构化对象(BaseModel)
        如何确保LLM一定能输出结构化对象。
        json_model(json_object)--保证输出JSON结构，提示词要求JSON内部字段结构。
        json_schema---物理层面保证输出的一定是遵循JSON_SCHEMA.无需在提示词中额外说明组（模型不支持）
        Funcation_calling：早期(保留下来)：自定义函数_最通用的
        Tool_calling:支持集成三方的工具函数以及并行执行,Agent推理速度响应都会更快
        :return:
        """
        # 1. 构建消息内容
        message_context = self._build_message_context(system_prompt, user_prompt)

        # 2. 定义模型实例
        chat_model = self.init_model_object(is_structured=True)

        structured_output = chat_model.with_structured_output(structed_object, method="json_schema")

        # 3. 调用模型
        try:
            llm_response = await structured_output.ainvoke(message_context)
        except Exception as exec:
            raise ValueError(f"{self.model_name}调用失败，原因:{str(exec)}")

        if llm_response is None:
            raise ValueError(f"{self.model_name}输出结构化对象为None")
        # 4. 将最终结果返回出去
        return llm_response

    def _build_message_context(self,
                               system_prompt: str,
                               user_prompt: str) -> list[BaseMessage]:
        """
        职责：将系统提示词和用户提示词封装成LangChain统一的消息类型
        注意：消息对象的内容不能在有模版变量
        :param system_prompt:
        :param user_prompt:
        :return:
        """
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

    def init_model_object(self, is_structured: bool = False) -> BaseChatModel:

        # kimi-k3模型的思考模型禁用掉
        model_name = self.model_name.lower()
        kwargs: dict[str, Any] = {}
        if is_structured and (  "kimi" in model_name or   "moonshot" in model_name):
            kwargs['extra_body'] = {
                "thinking": {
                    "type": "disabled"
                }
            }
        return init_chat_model(
            model_provider=self.model_provider,
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            **kwargs
        )


async def main_test():
    llm_client = LLMClient.from_role(role="insight_agent")

    llm_result = await  llm_client.generate_text(system_prompt="你是一个大语言模型专家",
                                                 user_prompt="请你给我解释LangChain以及LangGraph是什么以及都有哪些使用场景?")

    print(llm_result)


if __name__ == '__main__':
    asyncio.run(main_test())

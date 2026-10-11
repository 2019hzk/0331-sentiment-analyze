"""
作用：为异步模型调用提供指数退避重试
"""
import asyncio
from dataclasses import dataclass
from functools import wraps

from loguru import logger


@dataclass(slots=True)
class RetryConfig:
    init_delay: float = 1.0
    max_delay: float = 60.0  # 控制重试次数过多，重试时间太长
    max_retry: int = 3
    backoff_factor: float = 2.0

    def get_retry_delay(self, func_name: str, exc: Exception, attempt: int) -> float | None:
        """
        职责：获取重试延时，若不满足重试条件或达到最大次数则返回 None
        """
        # 1. 检查是否满足重试条件
        if not self._is_retryable(exc):
            return None

        # 2. 计算下一次重试延迟时间
        delay = self._compute_retry_delay(attempt)

        logger.warning(f"函数 {func_name} 调用失败 ({exc})，将在 {delay:.1f}s 后进行第 {attempt + 1}次重试...")
        return delay

    def _compute_retry_delay(self, attempt: int) -> float:
        """根据重试次数计算指数退避延迟时间"""
        return min(self.init_delay * (self.backoff_factor ** attempt), self.max_delay)

    def _extract_status_code(self, exc: Exception) -> int | None:
        """从异常对象或 HTTP 响应中提取状态码"""
        code = getattr(exc, "status_code", None)
        if code is not None:
            return code
        response = getattr(exc, "response", None)
        return getattr(response, "status_code", None)

    def _is_retryable(self, exc: Exception) -> bool:
        """
        职责：判断当前异常是否允许重试
        规则：只有明确是 4xx 客户端错误（且不是 429 限流）时才不重试；
              5xx 服务端错误、429 限流、网络超时/断网（code 为 None）均允许重试。
        """
        status_code = self._extract_status_code(exc)

        # 4xx 客户端错误（排除 429）代表请求参数或权限问题，重试毫无意义，直接放弃
        if isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429:
            return False

        return True


retry_config = RetryConfig()


def with_retry(func):
    """
    装饰器：对目标异步函数进行指数退避重试
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError("重试器只能修饰异步函数")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        last_exception: Exception | None = None

        for attempt in range(retry_config.max_retry):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                last_exception = exc
                delay = retry_config.get_retry_delay(
                    func_name=func.__name__,
                    exc=exc,
                    attempt=attempt
                )

                # 若无延迟时间，说明属于不可重试异常或已达最大重试次数，终止重试循环
                if delay is None:
                    break

                await asyncio.sleep(delay)

        # 达到最大重试次数或无法重试时抛出异常
        raise ValueError(f"函数 {func.__name__} 调用失败或无需重试，原因: {last_exception}") from last_exception

    return wrapper

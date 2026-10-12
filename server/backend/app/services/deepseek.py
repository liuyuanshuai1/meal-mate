import asyncio
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.core.response import AppException

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def _request_json(system_prompt: str, user_data: object, max_tokens: int, timeout: int = 20) -> dict[str, object]:
    settings = get_settings()
    if not settings.deepseek_api_key:
        raise AppException(50300, "推荐服务尚未配置")
    body = json.dumps(
        {
            "model": settings.deepseek_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_data, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "max_tokens": max_tokens,
            "stream": False,
        },
        ensure_ascii=False,
    ).encode()
    request = Request(
        DEEPSEEK_URL,
        data=body,
        headers={"Authorization": f"Bearer {settings.deepseek_api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            result = json.load(response)
        choice = result["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError("DeepSeek response incomplete")
        content = choice["message"]["content"]
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("DeepSeek response is not an object")
        return parsed
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise AppException(50300, "暂时无法生成推荐，请稍后再试") from exc


async def request_json(
    system_prompt: str, user_data: object, max_tokens: int = 900, timeout: int = 20
) -> dict[str, object]:
    return await asyncio.to_thread(_request_json, system_prompt, user_data, max_tokens, timeout)

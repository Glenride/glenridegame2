"""Logging helpers for handler instrumentation."""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from telegram import Update
from telegram.ext import ContextTypes

P = ParamSpec("P")
T = TypeVar("T")

HandlerFunc = Callable[P, Awaitable[T]]


def instrument_handler(handler_name: str | None = None) -> Callable[[HandlerFunc], HandlerFunc]:
    """Decorator to log latency and errors for async handlers."""

    def decorator(func: HandlerFunc) -> HandlerFunc:
        name = handler_name or func.__name__
        logger = logging.getLogger("bot.handlers")
        metrics_logger = logging.getLogger("bot.metrics")

        @wraps(func)
        async def wrapper(
            update: Update | None,
            context: ContextTypes.DEFAULT_TYPE,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> T:  # type: ignore[override]
            start = time.perf_counter()
            user = getattr(update, "effective_user", None)
            chat = getattr(update, "effective_chat", None)
            user_id = getattr(user, "id", None)
            chat_id = getattr(chat, "id", None)
            update_type = update.__class__.__name__ if update else None

            try:
                return await func(update, context, *args, **kwargs)
            except Exception as exc:
                logger.exception(
                    "handler_error",
                    extra={
                        "handler": name,
                        "user_id": user_id,
                        "chat_id": chat_id,
                    },
                )
                metrics_logger.error(
                    "handler_error_metric",
                    extra={
                        "metric": "handler_errors",
                        "handler": name,
                        "update_type": update_type,
                        "user_id": user_id,
                        "chat_id": chat_id,
                        "error_type": exc.__class__.__name__,
                    },
                )
                raise
            finally:
                latency_ms = (time.perf_counter() - start) * 1000
                latency_payload = {
                    "handler": name,
                    "latency_ms": round(latency_ms, 2),
                    "update_type": update_type,
                    "user_id": user_id,
                    "chat_id": chat_id,
                }
                logger.info("handler_complete", extra=latency_payload)
                metrics_logger.info(
                    "handler_latency_metric",
                    extra={"metric": "handler_latency_ms", **latency_payload},
                )

        return wrapper  # type: ignore[return-value]

    return decorator


__all__ = ["instrument_handler"]

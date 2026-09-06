import os
import time

from fastapi import HTTPException, Request


# Store request timestamps by client IP
_request_history: dict[str, list[float]] = {}


def rate_limit(
    request: Request,
    max_requests: int = 60,
    window_seconds: int = 60,
):
    # Disable rate limiting during pytest
    if os.getenv("PYTEST_CURRENT_TEST"):
        return

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    current_time = time.time()

    request_times = _request_history.get(
        client_ip,
        [],
    )

    # Remove requests outside the current window
    request_times = [
        request_time
        for request_time in request_times
        if current_time - request_time < window_seconds
    ]

    if len(request_times) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many requests. "
                "Please try again later."
            ),
        )

    request_times.append(current_time)

    _request_history[client_ip] = request_times
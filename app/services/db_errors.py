from collections.abc import Callable

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def with_integrity_handling[T](action: Callable[[], T], detail: str) -> T:
    """Translate SQL integrity errors into HTTP 409 errors.

    Args:
        action: Callable performing database write operations.
        detail: Conflict message returned to API clients.

    Returns:
        T: Value returned by ``action`` when no integrity error occurs.

    Raises:
        HTTPException: If an integrity constraint is violated.
    """
    try:
        return action()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from None

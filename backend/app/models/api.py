from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response envelope used across all endpoints.

    Attributes:
        status (str): Response status ("success" or "error")
        data (dict, optional): Response payload data
        message (str, optional): Human-readable message about the response
    """

    status: str
    data: dict = None
    message: str = None

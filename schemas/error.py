from pydantic import BaseModel


class ErrorSchema(BaseModel):
    """Standard error response structure for the API.

    This schema allows clients to parse and display errors consistently.
    The `message` field contains a human-readable error description.
    Additional fields (for example, `code` or `details`) can be added later.
    """

    message: str
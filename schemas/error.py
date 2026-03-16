from pydantic import BaseModel


# Defines the standard error response structure for the API.
# Keeps error handling consistent through a single human-readable message field.
class ErrorSchema(BaseModel):

    message: str
from pydantic import BaseModel


class ContextRatingModel(BaseModel):
    needs_web_search: bool

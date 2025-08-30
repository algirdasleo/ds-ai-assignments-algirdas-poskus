from pydantic import BaseModel


class QueryImprovementModel(BaseModel):
    improved_query: str

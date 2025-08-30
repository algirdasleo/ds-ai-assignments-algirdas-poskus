from pydantic import BaseModel


class PromptTopicModel(BaseModel):
    is_ai_ml_related: bool

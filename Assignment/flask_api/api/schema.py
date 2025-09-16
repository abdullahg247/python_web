from pydantic import BaseModel, field_validator

class EventIn(BaseModel):
    kind: str  # "manual" | "random"

    @field_validator("kind")
    @classmethod
    def valid_kind(cls, v):
        if v not in {"manual", "random"}:
            raise ValueError("kind must be 'manual' or 'random'")
        return v

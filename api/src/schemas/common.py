from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    """Base Pydantic Model"""

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        validate_assignment=True,
    )


class ResultSchema(Base):
    result: str

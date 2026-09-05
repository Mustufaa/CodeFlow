from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)


class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {
        "from_attributes": True,
    }
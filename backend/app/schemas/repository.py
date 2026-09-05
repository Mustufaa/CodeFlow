from pydantic import BaseModel, ConfigDict


class RepositoryConnect(BaseModel):
    owner: str
    name: str


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    github_installation_id: int
    github_repository_id: int
    owner: str
    name: str
    full_name: str
    private: bool
    default_branch: str
from pydantic import BaseModel, ConfigDict


class GitHubInstallationConnect(BaseModel):
    installation_id: int


class GitHubInstallationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    installation_id: int
    account_login: str
    account_type: str
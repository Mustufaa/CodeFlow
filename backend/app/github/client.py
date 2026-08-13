import httpx

from app.github.auth import get_installation_access_token


GITHUB_API_URL = "https://api.github.com"


class GitHubClient:
    """
    Client for interacting with GitHub API
    using a GitHub App installation token.
    """

    async def get_repository(
        self,
        installation_id: int,
        owner: str,
        repo: str,
    ) -> dict:

        access_token = await get_installation_access_token(
            installation_id
        )

        url = (
            f"{GITHUB_API_URL}/repos/"
            f"{owner}/{repo}"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
            )

        if response.status_code != 200:
            raise RuntimeError(
                "Failed to fetch GitHub repository: "
                f"{response.status_code} {response.text}"
            )

        return response.json()
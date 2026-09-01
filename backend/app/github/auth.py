import time
from pathlib import Path

import httpx
import jwt

from app.core.config import settings


GITHUB_API_URL = "https://api.github.com"


def create_github_app_jwt() -> str:
    """
    Create a JWT used to authenticate as the GitHub App.
    """

    if not settings.GITHUB_APP_ID:
        raise ValueError(
            "GITHUB_APP_ID is not configured."
        )

    if not settings.GITHUB_PRIVATE_KEY_PATH:
        raise ValueError(
            "GITHUB_PRIVATE_KEY_PATH is not configured."
        )

    # Resolve private key path relative to the backend directory
    private_key_path = Path(
        settings.GITHUB_PRIVATE_KEY_PATH
    )

    if not private_key_path.is_absolute():
        private_key_path = (
            Path(__file__).resolve().parents[2]
            / private_key_path
        )

    if not private_key_path.exists():
        raise FileNotFoundError(
            f"GitHub private key file not found: "
            f"{private_key_path}"
        )

    # Read GitHub App private key
    private_key = private_key_path.read_text(
        encoding="utf-8"
    )

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": settings.GITHUB_APP_ID,
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )

    return token


async def get_github_app() -> dict:
    """
    Get GitHub App information using the App JWT.
    Used to verify that GitHub App authentication works.
    """

    app_jwt = create_github_app_jwt()

    url = f"{GITHUB_API_URL}/app"

    headers = {
        "Authorization": f"Bearer {app_jwt}",
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
            "Failed to authenticate GitHub App: "
            f"{response.status_code} {response.text}"
        )

    return response.json()

async def get_github_app_installations() -> list:
    """
    Get all installations of the GitHub App.
    """

    app_jwt = create_github_app_jwt()

    url = f"{GITHUB_API_URL}/app/installations"

    headers = {
        "Authorization": f"Bearer {app_jwt}",
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
            "Failed to fetch GitHub App installations: "
            f"{response.status_code} {response.text}"
        )

    return response.json()

async def get_installation_access_token(
    installation_id: int,
) -> str:
    """
    Generate an installation access token
    for a GitHub App installation.
    """

    app_jwt = create_github_app_jwt()

    url = (
        f"{GITHUB_API_URL}/app/installations/"
        f"{installation_id}/access_tokens"
    )

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
        )

    if response.status_code != 201:
        raise RuntimeError(
            "Failed to create GitHub installation "
            "access token: "
            f"{response.status_code} {response.text}"
        )

    data = response.json()

    return data["token"]
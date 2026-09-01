import hashlib
import hmac

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings

from app.github.auth import (
    get_github_app,
    get_github_app_installations,
    get_installation_access_token,
    get_repository_installation_id,
)

from app.github.client import GitHubClient

from app.services.diff_service import build_review_file

from app.services.review_service import (
    review_changed_files,
)

from app.services.github_review_service import (
    post_review_to_github,
)


router = APIRouter(
    prefix="/api/github",
    tags=["GitHub"],
)


# ============================================================
# WEBHOOK SIGNATURE VERIFICATION
# ============================================================

def verify_github_signature(
    payload: bytes,
    signature: str | None,
) -> bool:
    """
    Verify that the webhook request came from GitHub.
    """

    if not signature:
        return False

    if not settings.GITHUB_WEBHOOK_SECRET:
        return False

    expected_signature = (
        "sha256="
        + hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


# ============================================================
# TEST GITHUB APP AUTHENTICATION
# ============================================================

@router.get("/test-app")
async def test_github_app():
    """
    Test GitHub App authentication.
    """

    try:
        app_data = await get_github_app()

        return {
            "message": (
                "GitHub App authentication successful"
            ),
            "app_id": app_data.get("id"),
            "name": app_data.get("name"),
            "slug": app_data.get("slug"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GET GITHUB APP INSTALLATIONS
# ============================================================

@router.get("/installations")
async def get_installations():
    """
    Get installations of the Softistry Code Reviewer
    GitHub App.
    """

    try:
        installations = (
            await get_github_app_installations()
        )

        return {
            "count": len(installations),
            "installations": [
                {
                    "id": installation.get("id"),
                    "account": installation.get(
                        "account",
                        {},
                    ).get("login"),
                    "account_type": installation.get(
                        "account",
                        {},
                    ).get("type"),
                }
                for installation in installations
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GET INSTALLATION ACCESS TOKEN
# ============================================================

@router.get(
    "/installations/{installation_id}/token"
)
async def get_installation_token(
    installation_id: int,
):
    """
    Test GitHub Installation Access Token generation.

    IMPORTANT:
    This endpoint should be removed or protected before
    production because it returns a GitHub credential.
    """

    try:
        token = await get_installation_access_token(
            installation_id
        )

        return {
            "message": (
                "Installation access token "
                "generated successfully"
            ),
            "installation_id": installation_id,
            "token": token,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GET REPOSITORY
# ============================================================

@router.get(
    "/repository/{owner}/{repo}"
)
async def get_repository(
    owner: str,
    repo: str,
):
    """
    Test repository access using the GitHub App.
    """

    installation_id = await get_repository_installation_id(
    owner=owner,
    repo=repo,
)

    try:
        client = GitHubClient()

        repository = await client.get_repository(
            installation_id=installation_id,
            owner=owner,
            repo=repo,
        )

        return {
            "message": (
                "Repository access successful"
            ),
            "repository": {
                "id": repository.get("id"),
                "name": repository.get("name"),
                "full_name": repository.get(
                    "full_name"
                ),
                "private": repository.get(
                    "private"
                ),
                "default_branch": repository.get(
                    "default_branch"
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GET PULL REQUEST
# ============================================================

@router.get(
    "/repository/{owner}/{repo}/pull/{pull_number}"
)
async def get_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Test Pull Request access using the GitHub App.
    """

    installation_id = await get_repository_installation_id(
    owner=owner,
    repo=repo,
)

    try:
        client = GitHubClient()

        pull_request = await client.get_pull_request(
            installation_id=installation_id,
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )

        return {
            "message": (
                "Pull Request access successful"
            ),
            "pull_request": {
                "number": pull_request.get(
                    "number"
                ),
                "title": pull_request.get(
                    "title"
                ),
                "state": pull_request.get(
                    "state"
                ),
                "user": pull_request.get(
                    "user",
                    {},
                ).get("login"),
                "base_branch": pull_request.get(
                    "base",
                    {},
                ).get("ref"),
                "head_branch": pull_request.get(
                    "head",
                    {},
                ).get("ref"),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GET & PROCESS PULL REQUEST FILES
# ============================================================

@router.get(
    "/repository/{owner}/{repo}/pull/{pull_number}/files"
)
async def get_pull_request_files(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Get files changed in a Pull Request
    and convert their patches into a
    review-ready structure.
    """

    installation_id = await get_repository_installation_id(
    owner=owner,
    repo=repo,
)

    try:
        client = GitHubClient()

        files = await client.get_pull_request_files(
            installation_id=installation_id,
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )

        review_files = [
            build_review_file(
                filename=file.get("filename"),
                status=file.get("status"),
                patch=file.get("patch"),
            )
            for file in files
        ]

        return {
            "message": (
                "Pull Request files "
                "processed successfully"
            ),
            "count": len(review_files),
            "files": review_files,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# AI REVIEW + GITHUB INLINE COMMENTS
# ============================================================

@router.post(
    "/repository/{owner}/{repo}/pull/{pull_number}/review"
)
async def review_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
):
    """
    Complete AI code-review pipeline:

    GitHub PR
        ↓
    Changed files
        ↓
    Diff parser
        ↓
    Gemini
        ↓
    ReviewResult
        ↓
    GitHub inline review
    """

    installation_id = await get_repository_installation_id(
    owner=owner,
    repo=repo,
)

    try:
        client = GitHubClient()

        # ----------------------------------------------------
        # 1. Fetch Pull Request files
        # ----------------------------------------------------

        files = await client.get_pull_request_files(
            installation_id=installation_id,
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )

        # ----------------------------------------------------
        # 2. Convert GitHub patches into structured files
        # ----------------------------------------------------

        review_files = [
            build_review_file(
                filename=file.get("filename"),
                status=file.get("status"),
                patch=file.get("patch"),
            )
            for file in files
        ]

        # ----------------------------------------------------
        # 3. Send changed code to Gemini
        # ----------------------------------------------------

        review_result = await review_changed_files(
            review_files
        )

        # ----------------------------------------------------
        # 4. Post findings to GitHub
        # ----------------------------------------------------

        github_review = await post_review_to_github(
            installation_id=installation_id,
            owner=owner,
            repo=repo,
            pull_number=pull_number,
            review_result=review_result,
        )

        # ----------------------------------------------------
        # 5. Return complete result
        # ----------------------------------------------------

        return {
            "message": (
                "Pull Request reviewed and "
                "GitHub review posted successfully"
            ),
            "repository": f"{owner}/{repo}",
            "pull_request": pull_number,
            "review": review_result.model_dump(),
            "github_review": github_review,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GITHUB WEBHOOK
# ============================================================

@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(
        default=None,
    ),
):
    """
    Receive, verify, and process GitHub webhook events.

    Pull Request events with actions:
        - opened
        - synchronize
        - reopened

    automatically trigger the AI code-review pipeline.
    """

    payload = await request.body()

    # --------------------------------------------------------
    # 1. Verify GitHub signature
    # --------------------------------------------------------

    if not verify_github_signature(
        payload,
        x_hub_signature_256,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub webhook signature.",
        )

    data = await request.json()

    event = request.headers.get(
        "X-GitHub-Event"
    )

    action = data.get("action")

    # --------------------------------------------------------
    # 2. Only process relevant Pull Request events
    # --------------------------------------------------------

    review_actions = {
        "opened",
        "synchronize",
        "reopened",
    }

    if event != "pull_request" or action not in review_actions:
        return {
            "message": "Webhook received but no review triggered.",
            "event": event,
            "action": action,
        }

    # --------------------------------------------------------
    # 3. Extract installation and repository information
    # --------------------------------------------------------

    installation_id = (
        data.get("installation", {})
        .get("id")
    )

    repository = data.get("repository", {})

    owner = (
        repository.get("owner", {})
        .get("login")
    )

    repo = repository.get("name")

    pull_number = data.get("number")

    if not installation_id:
        raise HTTPException(
            status_code=400,
            detail="GitHub installation ID missing from webhook payload.",
        )

    if not owner or not repo or not pull_number:
        raise HTTPException(
            status_code=400,
            detail="Repository or Pull Request information missing from webhook payload.",
        )

    # --------------------------------------------------------
    # 4. Fetch changed files
    # --------------------------------------------------------

    client = GitHubClient()

    files = await client.get_pull_request_files(
        installation_id=installation_id,
        owner=owner,
        repo=repo,
        pull_number=pull_number,
    )

    # --------------------------------------------------------
    # 5. Build review-ready files
    # --------------------------------------------------------

    review_files = [
        build_review_file(
            filename=file.get("filename"),
            status=file.get("status"),
            patch=file.get("patch"),
        )
        for file in files
    ]

    # --------------------------------------------------------
    # 6. Run AI review
    # --------------------------------------------------------

    review_result = await review_changed_files(
        review_files
    )

    # --------------------------------------------------------
    # 7. Post inline review to GitHub
    # --------------------------------------------------------

    github_review = await post_review_to_github(
        installation_id=installation_id,
        owner=owner,
        repo=repo,
        pull_number=pull_number,
        review_result=review_result,
    )

    # --------------------------------------------------------
    # 8. Return processing result
    # --------------------------------------------------------

    return {
        "message": "GitHub Pull Request reviewed successfully.",
        "event": event,
        "action": action,
        "repository": f"{owner}/{repo}",
        "pull_request": pull_number,
        "installation_id": installation_id,
        "review": review_result.model_dump(),
        "github_review": github_review,
    }
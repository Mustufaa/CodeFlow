import hashlib
import hmac

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings


router = APIRouter(
    prefix="/api/github",
    tags=["GitHub"],
)


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


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(
        default=None,
    ),
):
    payload = await request.body()

    # Verify GitHub signature
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

    return {
        "message": "GitHub webhook received",
        "event": event,
        "action": data.get("action"),
    }
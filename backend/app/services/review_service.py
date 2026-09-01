from app.schemas.review import ReviewResult
from app.services.gemini_service import review_code_with_gemini


def build_review_input(
    files: list[dict],
) -> str:
    """
    Convert structured GitHub PR files into
    a prompt-ready format for Gemini.
    """

    sections: list[str] = []

    for file in files:
        filename = file.get("filename", "")
        status = file.get("status", "")

        changed_lines = file.get(
            "changed_lines",
            [],
        )

        sections.append(
            f"File: {filename}\n"
            f"Status: {status}\n"
            f"Changed lines:"
        )

        for changed_line in changed_lines:
            line_number = changed_line.get("line")
            content = changed_line.get(
                "content",
                "",
            )

            sections.append(
                f"Line {line_number}: {content}"
            )

        sections.append("")

    return "\n".join(sections)


async def review_changed_files(
    files: list[dict],
) -> ReviewResult:
    """
    Review structured Pull Request changes
    using Gemini 3 Flash.
    """

    review_input = build_review_input(files)

    return await review_code_with_gemini(
        review_input
    )
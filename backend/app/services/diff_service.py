import re


HUNK_HEADER_PATTERN = re.compile(
    r"@@ -(?P<old_start>\d+)"
    r"(?:,(?P<old_count>\d+))?"
    r" \+(?P<new_start>\d+)"
    r"(?:,(?P<new_count>\d+))? @@"
)


def parse_patch(patch: str | None) -> list[dict]:
    """
    Parse a GitHub unified diff patch.

    Returns only added/changed lines because these are
    the lines where GitHub can place inline review comments.
    """

    if not patch:
        return []

    changed_lines: list[dict] = []

    current_new_line = None

    for line in patch.splitlines():
        # Detect a new diff hunk
        match = HUNK_HEADER_PATTERN.match(line)

        if match:
            current_new_line = int(
                match.group("new_start")
            )
            continue

        # Ignore diff metadata
        if line.startswith("\\ No newline"):
            continue

        if current_new_line is None:
            continue

        # Added line
        if line.startswith("+"):
            changed_lines.append(
                {
                    "line": current_new_line,
                    "content": line[1:],
                    "type": "added",
                }
            )

            current_new_line += 1

        # Deleted line
        elif line.startswith("-"):
            # Deleted lines do not exist in the new file,
            # so there is no new-file line number to comment on.
            continue

        # Context / unchanged line
        else:
            current_new_line += 1

    return changed_lines


def build_review_file(
    filename: str,
    status: str,
    patch: str | None,
) -> dict:
    """
    Convert a GitHub changed-file response into a
    review-ready structure.
    """

    changed_lines = parse_patch(patch)

    return {
        "filename": filename,
        "status": status,
        "changed_lines": changed_lines,
    }
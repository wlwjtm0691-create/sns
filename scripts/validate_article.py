#!/usr/bin/env python3
"""Validate a blog article folder and safely promote draft.md to final.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_REVIEW_ITEMS = (
    "조사 출처의 원문을 확인했고 핵심 주장과 일치함",
    "수치, 날짜, 인용, 고유명사를 출처와 대조함",
    "출처 없는 주장을 삭제하거나 불확실성 표시함",
    "문체, 구조, 중복, 맞춤법을 검수함",
    "최종 원고와 출처 링크를 점검함",
)
PLACEHOLDER_PATTERNS = (
    (re.compile(r"\bTODO\b", re.IGNORECASE), "TODO"),
    (re.compile(r"\bTBD\b", re.IGNORECASE), "TBD"),
    (re.compile(r"\[출처\s*필요\]"), "[출처 필요]"),
    (re.compile(r"\[확인\s*필요\]"), "[확인 필요]"),
    (re.compile(r"lorem ipsum", re.IGNORECASE), "lorem ipsum"),
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(https?://[^)\s]+\)")


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        errors.append(f"파일을 읽을 수 없습니다: {path.name} ({exc})")
        return ""


def check_placeholders(path: Path, content: str, errors: list[str]) -> None:
    for pattern, label in PLACEHOLDER_PATTERNS:
        if pattern.search(content):
            errors.append(f"{path.name}: 임시 문구가 남아 있습니다 ({label})")


def validate(folder: Path, promote: bool) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    names = ["brief.md", "research.md", "draft.md", "review.md"]
    contents = {name: read_text(folder / name, errors) for name in names}

    for name in names:
        if not (folder / name).is_file():
            errors.append(f"필수 파일이 없습니다: {name}")
        elif not contents[name].strip():
            errors.append(f"파일이 비어 있습니다: {name}")
        else:
            check_placeholders(folder / name, contents[name], errors)

    if contents["research.md"] and not MARKDOWN_LINK.search(contents["research.md"]):
        errors.append("research.md: 출처 Markdown 링크가 없습니다")

    review = contents["review.md"]
    for item in REQUIRED_REVIEW_ITEMS:
        if not re.search(rf"(?m)^-\s*\[x\]\s*{re.escape(item)}\s*$", review):
            errors.append(f"review.md: 검수 항목이 완료되지 않았습니다: {item}")

    final_path = folder / "final.md"
    if promote:
        if final_path.exists():
            errors.append("final.md가 이미 있습니다. 기존 원고를 덮어쓰지 않습니다.")
        draft = contents["draft.md"]
        if draft and not MARKDOWN_LINK.search(draft):
            errors.append("draft.md: 원고에 출처 Markdown 링크가 없습니다")
    else:
        if not final_path.is_file():
            errors.append("final.md가 없습니다. 검수 완료 후 --promote로 생성하세요.")
        else:
            final = read_text(final_path, errors)
            if not final.strip():
                errors.append("final.md가 비어 있습니다.")
            check_placeholders(final_path, final, errors)
            if final and not MARKDOWN_LINK.search(final):
                errors.append("final.md: 원고에 출처 Markdown 링크가 없습니다")

    return errors, contents


def main() -> int:
    parser = argparse.ArgumentParser(description="블로그 글 검수 및 최종 원고 승격")
    parser.add_argument("folder", type=Path, help="글 작업 폴더 경로")
    parser.add_argument(
        "--promote",
        action="store_true",
        help="검증 통과 시 draft.md를 새 final.md로 저장 (기존 파일은 덮어쓰지 않음)",
    )
    args = parser.parse_args()
    folder = args.folder.resolve()

    if not folder.is_dir():
        print(f"오류: 작업 폴더가 없습니다: {folder}", file=sys.stderr)
        return 2

    errors, contents = validate(folder, args.promote)
    if errors:
        print("검증 실패:")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.promote:
        final_path = folder / "final.md"
        try:
            # Exclusive create prevents accidental overwrites.
            with final_path.open("x", encoding="utf-8", newline="") as output:
                output.write(contents["draft.md"])
        except FileExistsError:
            print("오류: final.md가 이미 있습니다. 덮어쓰지 않았습니다.", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"오류: final.md를 저장하지 못했습니다: {exc}", file=sys.stderr)
            return 2
        print(f"검증 통과. 최종 원고를 생성했습니다: {final_path}")
    else:
        print(f"검증 통과: {folder / 'final.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

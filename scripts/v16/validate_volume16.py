#!/usr/bin/env python3
"""Validate the structural contract of the volume 16 manga-spread scripts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

EXPECTED = {
    121: "城井の使者",
    122: "谷の地図",
    123: "進軍命令",
    124: "伏せられた道",
    125: "谷底の旗",
    126: "敗走の米",
    127: "剃髪の朝",
    128: "同じ約束の亀裂",
}
EXPECTED_PAGE_COUNTS = {
    1: 1,
    2: 3,
    3: 6,
    4: 3,
    5: 3,
    6: 3,
    7: 6,
    8: 3,
    9: 2,
    10: 6,
    11: 3,
    12: 1,
}


def validate_file(path: Path, episode: int, title: str) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    expected_title = f'# 『戦帰 SENKI』v16ep{episode:02d}「{title}」'
    if not text.startswith(expected_title):
        errors.append(f"title mismatch: expected {expected_title!r}")

    page_matches = list(
        re.finditer(r"^## P(\d+)（(\d+)コマ(?:・[^）]+)?）$", text, flags=re.MULTILINE)
    )
    if len(page_matches) != 12:
        errors.append(f"expected 12 page headings, found {len(page_matches)}")
        return errors

    page_numbers = [int(match.group(1)) for match in page_matches]
    if page_numbers != list(range(1, 13)):
        errors.append(f"page sequence is {page_numbers}")

    for index, match in enumerate(page_matches):
        page_no = int(match.group(1))
        declared = int(match.group(2))
        start = match.end()
        end = page_matches[index + 1].start() if index + 1 < len(page_matches) else text.find("\n---", start)
        page_text = text[start:end]
        actual = len(re.findall(r"^### c\d+［", page_text, flags=re.MULTILINE))
        expected = EXPECTED_PAGE_COUNTS[page_no]
        if declared != expected:
            errors.append(f"P{page_no}: declared {declared}, expected {expected}")
        if actual != expected:
            errors.append(f"P{page_no}: found {actual} panels, expected {expected}")

    total = len(re.findall(r"^### c\d+［", text, flags=re.MULTILINE))
    if total != 40:
        errors.append(f"total panels {total}, expected 40")

    for page_no in (1, 12):
        heading = page_matches[page_no - 1]
        start = heading.end()
        end = page_matches[page_no].start() if page_no < 12 else text.find("\n---", start)
        if "［splash:bleed］" not in text[start:end]:
            errors.append(f"P{page_no}: missing splash:bleed")

    required_sections = (
        "## 話情報",
        "## 骨子",
        "## 紙面設計（工程3の自己申告）",
        "## 登場",
        "## この話の生成規約",
        "## 見開き対応（右綴じ）",
        f"# 第{episode}話終了時の台帳",
        "# manga-spread 運用メモ",
    )
    for section in required_sections:
        if section not in text:
            errors.append(f"missing section: {section}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parent
    all_errors: list[str] = []

    for episode, title in EXPECTED.items():
        path = root / f"ep{episode}_{title}.md"
        if not path.exists():
            all_errors.append(f"{path.name}: missing")
            continue
        errors = validate_file(path, episode, title)
        if errors:
            all_errors.extend(f"{path.name}: {error}" for error in errors)
        else:
            print(f"PASS {path.name}: 12 pages / 40 panels")

    if all_errors:
        print("\nFAILED", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("\nVolume 16 structural validation passed: 8 episodes / 96 pages / 320 panels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

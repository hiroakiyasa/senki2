#!/usr/bin/env python3
"""Validate Volume 6 manga production scripts.

Checks the fixed 12-page / 43-panel layout, required production fields,
sequential episode numbers, ledgers, and a small set of continuity locks.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_EPISODES = list(range(41, 49))
EXPECTED_PANEL_COUNTS = [1, 3, 7, 3, 3, 3, 7, 3, 2, 7, 3, 1]
EXPECTED_TOTAL_PAGES = 96
EXPECTED_TOTAL_PANELS = 344

CONTINUITY_LOCKS: dict[int, tuple[str, ...]] = {
    41: ("黒田の組紐", "左脇腹", "欠けた椀"),
    42: ("左足首", "百地カヤ", "スズ"),
    43: ("交代五人", "子供八人", "灰谷十蔵"),
    44: ("左前腕", "鴉丸", "借り"),
    45: ("黒田方", "左前腕", "仙石"),
    46: ("仙石札を受けない", "六台", "半刻遅れ"),
    47: ("三人の名", "五郎作", "左前腕傷"),
    48: ("黒田へ戻る", "正式小頭札", "備中"),
}

PAGE_RE = re.compile(r"^# P(\d+)（", re.MULTILINE)
PANEL_RE = re.compile(r"^### c(\d{2})［", re.MULTILINE)
EP_RE = re.compile(r"v06ep(\d{2})")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_file(path: Path, expected_ep: int) -> tuple[int, int, list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    title_match = EP_RE.search(text)
    if not title_match or int(title_match.group(1)) != expected_ep:
        fail(errors, f"{path.name}: title episode number is not {expected_ep}")

    if "12頁（6見開き・43コマ）" not in text:
        fail(errors, f"{path.name}: missing fixed page/panel declaration")

    page_matches = list(PAGE_RE.finditer(text))
    page_numbers = [int(match.group(1)) for match in page_matches]
    if page_numbers != list(range(1, 13)):
        fail(errors, f"{path.name}: page headings are {page_numbers}, expected 1..12")

    all_panels = list(PANEL_RE.finditer(text))
    if len(all_panels) != 43:
        fail(errors, f"{path.name}: {len(all_panels)} panel headings, expected 43")

    if len(page_matches) == 12:
        for index, match in enumerate(page_matches):
            start = match.end()
            end = page_matches[index + 1].start() if index + 1 < 12 else len(text)
            section = text[start:end]
            panels = list(PANEL_RE.finditer(section))
            expected = EXPECTED_PANEL_COUNTS[index]
            if len(panels) != expected:
                fail(
                    errors,
                    f"{path.name}: P{index + 1} has {len(panels)} panels, expected {expected}",
                )

            panel_numbers = [int(panel.group(1)) for panel in panels]
            if panel_numbers != list(range(1, expected + 1)):
                fail(
                    errors,
                    f"{path.name}: P{index + 1} panel numbering {panel_numbers}, "
                    f"expected 1..{expected}",
                )

    art_fields = len(re.findall(r"^画:", text, re.MULTILINE))
    generation_fields = len(re.findall(r"^生成:", text, re.MULTILINE))
    if art_fields != 43:
        fail(errors, f"{path.name}: {art_fields} art fields, expected 43")
    if generation_fields != 43:
        fail(errors, f"{path.name}: {generation_fields} generation fields, expected 43")

    if "終了時の台帳" not in text and "第6巻終了時の台帳" not in text:
        fail(errors, f"{path.name}: missing continuity ledger")

    if "<!--" in text or "制作脚本をこのファイルへ反映する" in text:
        fail(errors, f"{path.name}: placeholder or unfinished marker remains")

    sound_count = len(re.findall(r"^音「", text, re.MULTILINE))
    if sound_count < 9:
        fail(errors, f"{path.name}: only {sound_count} sound-effect fields; expected at least 9")

    for required in CONTINUITY_LOCKS[expected_ep]:
        if required not in text:
            fail(errors, f"{path.name}: continuity lock missing: {required}")

    return len(page_matches), len(all_panels), errors


def main() -> int:
    paths = sorted(ROOT.glob("ep??_*.md"))
    errors: list[str] = []

    if len(paths) != 8:
        fail(errors, f"found {len(paths)} episode files, expected 8")

    actual_numbers: list[int] = []
    total_pages = 0
    total_panels = 0

    for path in paths:
        match = re.match(r"ep(\d{2})_", path.name)
        if not match:
            fail(errors, f"unexpected filename: {path.name}")
            continue
        episode = int(match.group(1))
        actual_numbers.append(episode)
        pages, panels, file_errors = validate_file(path, episode)
        total_pages += pages
        total_panels += panels
        errors.extend(file_errors)
        status = "PASS" if not file_errors else "FAIL"
        print(f"{status}  ep{episode}: {pages} pages / {panels} panels / {path.name}")

    if actual_numbers != EXPECTED_EPISODES:
        fail(errors, f"episode sequence is {actual_numbers}, expected {EXPECTED_EPISODES}")
    if total_pages != EXPECTED_TOTAL_PAGES:
        fail(errors, f"total pages {total_pages}, expected {EXPECTED_TOTAL_PAGES}")
    if total_panels != EXPECTED_TOTAL_PANELS:
        fail(errors, f"total panels {total_panels}, expected {EXPECTED_TOTAL_PANELS}")

    print(f"TOTAL: {total_pages} pages / {total_panels} panels")

    if errors:
        print("\nValidation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Volume 6 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

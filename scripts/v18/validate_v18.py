#!/usr/bin/env python3
"""第18巻 manga-spread 制作脚本の構造・連続性を検査する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
EPISODES = [
    (137, "ep137_釜山の岸.md"),
    (138, "ep138_言葉のない村.md"),
    (139, "ep139_先鋒の仕事.md"),
    (140, "ep140_渡河点.md"),
    (141, "ep141_凍る米.md"),
    (142, "ep142_捕虜の地図.md"),
    (143, "ep143_川中の長政.md"),
    (144, "ep144_晋州へ.md"),
]
EXPECTED_PAGE_COUNTS = {
    1: 1,
    2: 3,
    3: 7,
    4: 3,
    5: 3,
    6: 3,
    7: 7,
    8: 2,
    9: 3,
    10: 7,
    11: 3,
    12: 1,
}


def parse_page_counts(text: str) -> dict[int, int]:
    counts: dict[int, int] = {}
    current_page: int | None = None
    for line in text.splitlines():
        page_match = re.match(r"^# P(\d+)\b", line)
        if page_match:
            current_page = int(page_match.group(1))
            counts.setdefault(current_page, 0)
            continue
        if current_page is not None and re.match(r"^### c\d{2}［", line):
            counts[current_page] += 1
    return counts


def has_any(text: str, alternatives: tuple[str, ...]) -> bool:
    return any(item in text for item in alternatives)


def check_episode(number: int, filename: str) -> tuple[list[str], dict[str, int], str]:
    errors: list[str] = []
    path = BASE / filename
    if not path.exists():
        return [f"missing: {filename}"], {}, ""

    text = path.read_text(encoding="utf-8")
    page_counts = parse_page_counts(text)
    panel_total = sum(page_counts.values())
    sounds = text.count('音「')
    shouts = text.count("叫び=")

    if page_counts != EXPECTED_PAGE_COUNTS:
        errors.append(f"page panel counts: {page_counts}")
    if panel_total != 43:
        errors.append(f"panel total: {panel_total} != 43")
    if sounds < 9:
        errors.append(f"sound panels: {sounds} < 9")
    if shouts < 3:
        errors.append(f"shouts: {shouts} < 3")
    if f"v18ep{number}" not in text.splitlines()[0]:
        errors.append("episode code/title mismatch")
    if f"# 第{number}話終了時の台帳" not in text:
        errors.append("ending ledger missing")
    if "## 見開き対応" not in text or "| S6 | P11 | P12 |" not in text:
        errors.append("spread table incomplete")
    if "可読文字" not in text:
        errors.append("readable-text generation ban missing")

    # The second repair ring and completed Kikkosha may be named only as a ban,
    # absence, or a future-volume handoff—not as a present accomplishment.
    for line_no, line in enumerate(text.splitlines(), 1):
        if "第二" in line and "補修輪" in line:
            allowed = any(token in line for token in ("禁=", "ない", "未", "第19巻", "送る", "禁止"))
            if not allowed:
                errors.append(f"line {line_no}: second repair ring introduced: {line}")
        if "亀甲車" in line:
            allowed = any(token in line for token in ("禁=", "第19巻", "正式", "先取り", "禁止"))
            if not allowed:
                errors.append(f"line {line_no}: completed Kikkosha introduced: {line}")

    metrics = {
        "pages": len(page_counts),
        "panels": panel_total,
        "sounds": sounds,
        "shouts": shouts,
    }
    return errors, metrics, text


def main() -> int:
    all_errors: list[str] = []
    texts: dict[int, str] = {}
    total_pages = total_panels = 0

    print("第18巻 制作脚本検品")
    print("=" * 72)

    for number, filename in EPISODES:
        errors, metrics, text = check_episode(number, filename)
        texts[number] = text
        if metrics:
            total_pages += metrics["pages"]
            total_panels += metrics["panels"]
            status = "PASS" if not errors else "FAIL"
            print(
                f"{status} {filename}: "
                f"{metrics['pages']}頁 / {metrics['panels']}コマ / "
                f"擬音{metrics['sounds']} / 叫び{metrics['shouts']}"
            )
        else:
            print(f"FAIL {filename}: file missing")
        all_errors.extend(f"{filename}: {err}" for err in errors)

    # Volume-level continuity.
    volume_checks: list[tuple[str, bool]] = [
        (
            "第137〜139話は黒槍組50人",
            all(has_any(texts[n], ("黒槍組50人", "黒槍組五十人", "五十人")) for n in (137, 138, 139)),
        ),
        (
            "第140話で庄兵衛死亡・49人",
            "庄兵衛" in texts[140]
            and "死亡" in texts[140]
            and has_any(texts[140], ("黒槍組は50人から49人", "四十九人")),
        ),
        (
            "第141話は49人",
            has_any(texts[141], ("黒槍組49人", "四十九人")),
        ),
        (
            "第142話で藤助死亡・48人",
            "藤助" in texts[142]
            and "死亡" in texts[142]
            and has_any(texts[142], ("黒槍組は49人から48人", "四十八人")),
        ),
        (
            "第143〜144話は48人",
            all(has_any(texts[n], ("黒槍組48人", "黒槍組四十八人", "四十八人")) for n in (143, 144)),
        ),
        (
            "右肩の後遺症を継続",
            all("右肩" in texts[n] for n in range(137, 145)),
        ),
        (
            "黒槍は第一補修輪のみ",
            all("第一" in texts[n] and "補修輪" in texts[n] for n in range(137, 145)),
        ),
        (
            "ハジュンは加入しない",
            has_any(texts[138], ("加入しない", "加入せず"))
            and has_any(texts[144], ("加入しない", "加入せず", "加入していない")),
        ),
        (
            "第144話は23人回収・動く屋根は着想のみ",
            "23人" in texts[144]
            and has_any(texts[144], ("泥図", "思いつ"))
            and "実物の移動屋根はまだ存在せず" in texts[144]
            and "第19巻" in texts[144]
            and "正式" in texts[144],
        ),
    ]

    print("-" * 72)
    for label, ok in volume_checks:
        print(f"{'PASS' if ok else 'FAIL'} {label}")
        if not ok:
            all_errors.append(f"volume continuity: {label}")

    if total_pages != 96:
        all_errors.append(f"volume pages: {total_pages} != 96")
    if total_panels != 344:
        all_errors.append(f"volume panels: {total_panels} != 344")

    print("-" * 72)
    print(f"合計: {total_pages}頁 / {total_panels}コマ")

    if all_errors:
        print("\n検品失敗:", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("全項目合格")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

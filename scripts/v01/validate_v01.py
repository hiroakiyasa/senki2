#!/usr/bin/env python3
"""Volume 1 production-script validator for SENKI.

Run from the repository root:
    python3 scripts/v01/validate_v01.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
FILES = [
    BASE / 'ep01_父のいない馬.md',
    BASE / 'ep02_城門の外.md',
    BASE / 'ep03_十二台の米.md',
    BASE / 'ep04_名の値段.md',
    BASE / 'ep05_焼け槍.md',
    BASE / 'ep06_五人で渡れ.md',
    BASE / 'ep07_仇か橋か.md',
    BASE / 'ep08_二人の大将.md',
]
EXPECTED_PANELS = {1: 43, 2: 42, 3: 42, 4: 42, 5: 42, 6: 42, 7: 42, 8: 42}
EXPECTED_FAST = {3, 7, 10}


@dataclass
class Result:
    errors: list[str]
    warnings: list[str]


def page_body(text: str) -> str:
    start = text.find('## P1（')
    end = text.find('# 第', start + 1)
    if start < 0:
        return ''
    return text[start:end if end >= 0 else None]


def page_sections(body: str) -> dict[int, str]:
    matches = list(re.finditer(r'^## P(\d+)（[^\n]*）\s*$', body, re.M))
    out: dict[int, str] = {}
    for i, match in enumerate(matches):
        number = int(match.group(1))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out[number] = body[match.start():end]
    return out


def validate_file(ep: int, path: Path) -> tuple[Result, dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return Result([f'missing file: {path.name}'], []), {}

    text = path.read_text(encoding='utf-8')
    body = page_body(text)
    pages = page_sections(body)
    panels = len(re.findall(r'^### c\d{2}［', body, re.M))
    sfx = len(re.findall(r'^音「', body, re.M))
    shouts = len(re.findall(r'\|叫び=[^|\n]+', body))
    splashes = len(re.findall(r'^### c\d{2}［splash:bleed］', body, re.M))

    if len(pages) != 12:
        errors.append(f'pages={len(pages)} expected=12')
    if panels != EXPECTED_PANELS[ep]:
        errors.append(f'panels={panels} expected={EXPECTED_PANELS[ep]}')
    if splashes != 2:
        errors.append(f'splash pages={splashes} expected=2')
    if sfx / max(panels, 1) < 0.20:
        errors.append(f'SFX ratio={sfx}/{panels} below 20%')
    if shouts < 3:
        errors.append(f'shouts={shouts} below 3')

    for page in range(1, 13):
        if page not in pages:
            continue
        count = len(re.findall(r'^### c\d{2}［', pages[page], re.M))
        if page in EXPECTED_FAST and count < 7:
            errors.append(f'P{page} fast page has {count} panels')
        if page in {1, 12} and count != 1:
            errors.append(f'P{page} must be one-panel page, got {count}')

    low_panel_pages = 0
    for section in pages.values():
        count = len(re.findall(r'^### c\d{2}［', section, re.M))
        if 2 <= count <= 3:
            low_panel_pages += 1
    if low_panel_pages < 4:
        errors.append(f'2–3 panel pages={low_panel_pages} below 4')

    # Timing of reveals: ignore generation-ban lines when checking what readers see.
    body_no_gen = '\n'.join(line for line in body.splitlines() if not line.startswith('生成:'))
    visual_lines = '\n'.join(line for line in body.splitlines() if line.startswith('画:'))
    if ep <= 3 and '焼け槍' in body_no_gen:
        errors.append('burned spear appears before episode 4/5 reveal')
    if ep <= 3 and '源六' in body_no_gen:
        errors.append('Genroku name appears before episode 4')
    if ep == 1:
        if '馬から飛び降り' in visual_lines or '馬の背から' in visual_lines:
            errors.append('episode 1 incorrectly depicts Matabei as riding')
        if '新左衛門が' in visual_lines or '新左衛門の顔' in visual_lines:
            errors.append('episode 1 depicts father directly')
    if ep == 4:
        p12 = pages.get(12, '')
        before = ''.join(pages.get(page, '') for page in range(1, 12))
        before_no_gen = '\n'.join(line for line in before.splitlines() if not line.startswith('生成:'))
        if '焼け槍' in before_no_gen:
            errors.append('episode 4 shows burned spear before P12')
        if '焼け槍' not in p12:
            errors.append('episode 4 P12 must reveal burned spear')
    if ep >= 5 and '焼け槍' not in body:
        errors.append('burned spear missing after inheritance')

    # Required volume continuity anchors.
    required = {
        1: ['四十三人', '十二台', '半分残し'],
        2: ['徒歩8', '3台', '札'],
        3: ['9台', '14俵', '一組目'],
        4: ['残り二十二', '左肩', '新左衛門'],
        5: ['残り十四', '四十二', '太一'],
        6: ['四十三', '九台', '五人とも'],
        7: ['四十三', '九台', '内門'],
        8: ['四十三', '九台', '仮札', '人質'],
    }[ep]
    for token in required:
        if token not in text:
            errors.append(f'missing continuity token: {token}')

    # Common image-generation constraints.
    if '生成画像へ文字' not in text and '画像へ文字' not in text:
        warnings.append('no explicit no-text generation reminder')
    if '可読文字' not in text and '文字なし' not in text:
        warnings.append('few explicit readable-text bans')

    # Crude Stop-Slop heuristics for narration/dialogue, not technical directions.
    prose_lines = '\n'.join(
        line for line in body.splitlines()
        if re.match(r'^(?:N|[^:：]{1,12})「', line)
    )
    binary = len(re.findall(r'ではない[。．]\s*[^\n]{0,25}(?:だ|です)', prose_lines))
    if binary > 2:
        warnings.append(f'formulaic binary contrast candidates={binary}')
    triplet_short = len(re.findall(r'(?:^|\n)(?:[^\n。]{1,16}。\s*){3}', prose_lines))
    if triplet_short > 2:
        warnings.append(f'staccato triplet candidates={triplet_short}')

    return Result(errors, warnings), {
        'pages': len(pages),
        'panels': panels,
        'sfx': sfx,
        'shouts': shouts,
        'low_pages': low_panel_pages,
        'splashes': splashes,
    }


def cross_validate() -> list[str]:
    errors: list[str] = []
    corpus = {
        episode: FILES[episode - 1].read_text(encoding='utf-8')
        for episode in range(1, 9)
        if FILES[episode - 1].exists()
    }
    if '父の栗毛：門脇の軒へ繋ぐ' not in corpus.get(2, ''):
        errors.append('ep2 must park father horse at gate-side eaves')
    if '12台→到着目標9台' not in corpus.get(3, ''):
        errors.append('ep3 must lock 12 carts to 9 arrival carts')
    if '左肩' not in corpus.get(4, '') or '左肩' not in corpus.get(5, ''):
        errors.append('left-shoulder injury continuity missing ep4→ep5')
    if '両掌' not in corpus.get(5, '') or '両掌' not in corpus.get(8, ''):
        errors.append('palm-injury continuity missing ep5→ep8')

    matabei_dream = '俺は、どんな負け戦でも、最後の一人まで連れて帰る大将になる'
    matsujumaru_dream = '帰ってきた者が、もう追い出されない場所を作ります'
    if matabei_dream not in corpus.get(8, ''):
        errors.append('Matabei fixed dream missing ep8')
    if matsujumaru_dream not in corpus.get(8, ''):
        errors.append('Matsujumaru fixed dream missing ep8')
    return errors


def main() -> int:
    all_errors: list[str] = []
    print('SENKI Volume 1 script audit')
    print('=' * 72)
    for episode, path in enumerate(FILES, 1):
        result, metrics = validate_file(episode, path)
        status = 'PASS' if not result.errors else 'FAIL'
        print(f'{status} ep{episode:02d} {path.name}: {metrics}')
        for message in result.errors:
            print(f'  ERROR: {message}')
            all_errors.append(f'ep{episode:02d}: {message}')
        for message in result.warnings:
            print(f'  WARN : {message}')

    for message in cross_validate():
        print(f'  ERROR: cross-volume: {message}')
        all_errors.append(message)

    print('=' * 72)
    if all_errors:
        print(f'FAILED: {len(all_errors)} error(s)')
        return 1
    print('PASSED: all 8 episodes, 96 pages, continuity gates satisfied')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

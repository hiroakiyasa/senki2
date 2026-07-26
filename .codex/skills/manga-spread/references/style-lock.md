# SENKI approved full-color style lock

## Authority order

1. Canon script: event, weather, time, emotion, props.
2. Approved character V1 sheet: identity, large-eye ratio, face, hair, age, clothing base.
3. Approved visual-asset sheet: castle layout, house plan, animal, weapon, vehicle, document.
4. `approved_style_anchor.png`: line, cel color, lighting, background density, action energy only.
5. Previous spread: short-range continuity only.

A lower authority source must never overwrite a higher one. Never copy the style-anchor character into the story.

## Non-negotiable render fingerprint

- Full color only.
- Bold black contour hierarchy with clean, readable silhouettes.
- Large expressive lovable eyes at every age; age never shrinks the eyes.
- Vivid cel shading with controlled local colors, warm sunlight, cool sky shadow, crisp value separation.
- Dynamic low and high camera angles, strong foreshortening, readable action arcs.
- Detailed Azuchi-Momoyama architecture and material culture; a background must work as a standalone illustration.
- Clothing is intact and rank appropriate. Wealth rises through weave, dye, silk, lacquer, lacing, fittings, horse tack, and retainers.
- The same character across ages keeps eye size, iris ratio, eye spacing, face outline, nose, mouth, chin, and defining hair structure.

## Spread fingerprint

- One generated landscape image equals two right-bound pages.
- Right half is read first, left half second.
- Keep the center gutter free of faces, eyes, dialogue areas, and canonical prop tips.
- Normal beats use clear rectangular panels.
- Decisive beats may use one dominant trapezoid, wedge, polygon, diagonal bleed, or cross-gutter environmental panel.
- The focal character may break a border with hair, arm, spear, cloak, or full silhouette.
- Use dark, unmistakable borders. Do not use faint seams that disappear into the art.
- Do not default to equal 4/5/6-panel grids.
- Never crop faces, hands, or required props. Intentional trim bleed must preserve the readable expression.

## Negative lock

No monochrome, desaturated wash, photorealism, copied anchor character, clone faces, small adult eyes, excessive aging, torn clothes, random rain, random sparks, blue aura, modern objects, Western saddle, fantasy castle, generated dialogue, pseudo-kanji, watermark, logo, or UI.

## Portable reference

Always resolve the anchor relative to this skill directory:

`references/approved_style_anchor.png`

Before generation, compare its SHA-256 with `references/approved_style_anchor.sha256`. A mismatch means the style is unapproved and generation must stop.

# SENKI character and world reference library

This directory is the canonical portable visual source for manga-spread generation in `senki2`.

- `index.html`: character-by-age review matrix. Model sheets use `object-fit: contain` and are not cropped.
- `images/<character-id>/`: all generated character model sheets. `v01.png` is the identity master for non-Matabei characters.
- `world_assets.html`: continuity inventory for castles, houses, battlefields, vehicles, weapons, documents, and daily-life objects. `設計済・未生成` is a plan, not an approved image.
- `manifest.json`: machine-readable byte size and SHA-256 for every committed PNG.
- `asset_reference_policy.md`: mandatory manga-spread lookup rules.

Do not replace an image in place without regenerating the manifest and obtaining approval.

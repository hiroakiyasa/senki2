---
name: manga-spread
description: 『戦帰 SENKI』の脚本から、承認済みフルカラー画風と、物語重要度に応じた自由なコマ面積・変形枠・人物越境を使い、見開き2ページを1枚で一括生成する。前ページ・人物・視覚資産・画風を参照ボードへ機械合成して一貫性を保つ。「見開きで作って」「漫画スプレッド」「ページ一括で速く作りたい」のとき使う。Codex CLIからも同じ手順で使える。
---

# 見開き一括生成スキル(manga-spread)

1コマずつ生成すると1話128コマで数時間かかる。**見開き2ページ(9〜10コマ)を1枚として生成**すると約4分/枚で済む(実測: `pipeline/test/pagebatch_ep03_p023_024_spread.png` 10コマ/約3分53秒)。速度と引き換えに1コマ単位のリテイクはできなくなる(崩れたら見開きごと作り直す)。

## この方式の核 — 参照ボード(1枚に統合)

画像生成AI(ChatGPTアプリ・GPT Image)は、参照画像を**複数枚バラバラに渡すと取り違える**(誰の顔か・どれが背景の基準か)。そこで、その見開きで統一すべき素材を `reference_board.mjs` が**1枚の画像**へ機械合成し、見出しラベルを付けて渡す。AIはこの1枚だけを見る。

ボードに載る4区画(あるものだけ):
1. **① 前ページ** = 直前の見開きの生成結果。部屋・背景・小道具・光・時刻の連続性の基準(コマ割りはコピーさせない)
2. **② 画風アンカー** = `references/approved_style_anchor.png`。太い線、鮮烈なセル塗り、光、背景密度だけ踏襲
3. **③ 登場人物シート** = 名前ラベル付き。顔・髪・年齢・衣装の唯一の正解
4. **④ 小道具シート** = 黒槍など、形状の基準

## 画風ロック（全工程より優先）

このスキルで生成する漫画は**絶対にフルカラー**とし、次の承認アンカーを毎回使う。

- 必須アンカー: `references/approved_style_anchor.png`
- 整合性記録: `references/approved_style_anchor.sha256`
- 詳細仕様: [references/style-lock.md](references/style-lock.md)
- 人物参照manifest: `production/character_bible/manifest.json`
- 人物一覧: `production/character_bible/index.html`
- 世界・小道具台帳: `production/character_bible/world_assets.html`
- 各見開きのprepare前に人物IDと年代版をmanifestから解決し、該当PNGを参照ボード③へ必ず入れる。非又兵衛の`v01.png`は顔の絶対マスター。必要年代版が未生成なら本編で顔を即興せず停止する。
- 世界・小道具台帳の`設計済・未生成`は画像参照に使わない。実画像と承認記録がある資産だけを参照ボード④へ入れる。
- アンカーは線、彩色、光、背景密度、画面の勢いだけを示す。アンカー内の人物の顔、髪、服、ポーズはコピーしない。
- 人物の顔と衣装は承認済みV1人物シートをアンカーより強い正解として扱う。
- 太く切れ味のある黒い主線、鮮烈なセル画色、大きく表情豊かな目、強い明暗差を固定する。
- 安土桃山期の木、土壁、藁、漆、鉄、革、麻、木綿、絹を高密度に描き、背景だけでも一枚の作品として成立させる。
- 衣服は身分相応で破れていない。出世は織り、染め、金襴、漆、威糸、金具、馬具、従者数で示す。
- 雨・夜・霧は脚本にある時だけ使う。暗場でも顔と衣装色を読める露出を保つ。

### 自由コマ設計

- 通常の会話・移動・説明は読みやすい長方形にする。
- 発見・決断・衝撃・戦闘の転換点は台形、斜辺、多角形、裁ち落としを使い、見開き面積の40〜65%を与えてよい。
- 補助反応は15〜25%、瞬間挿入は5〜12%。均等な4・5・6コマ割りを既定にしない。見開きの9〜10コマも重要度に従い面積を不均等にする。
- コマ境界は黒または濃色で明瞭にし、完成B5換算8〜16px相当。背景へ溶ける薄い境界は禁止。
- 主役の顔、腕、髪、槍、陣羽織は重要場面に限り枠を越えてよい。ただし別時間の人物へ誤接続させない。
- 顔、手、重要武器は断裁で欠けさせない。中央ノドへ顔、目、台詞予定域、重要武器の先端を置かない。

### 画像生成へ渡す固定プロンプト契約

`sNN.instruction.txt` の場面固有記述より前に、次を必ず含める。

```text
FULL-COLOR Japanese shonen manga double-page spread for SENKI.
Use the approved style anchor only for bold linework, vivid cel color, large expressive eyes,
strong daylight/value separation, energetic foreshortening, and museum-quality Azuchi-Momoyama backgrounds.
Do not copy any character from the style anchor. Character sheets are the absolute identity source.
Right half is the earlier page; left half is the later page; keep the center gutter safe.
Use clear dark panel borders. Ordinary beats use rectangles; decisive beats may use large polygonal or bleed panels.
Allow the focal character, hair, arm, spear, or cloak to break a panel border when narratively important.
Never crop faces, hands, or canonical props. No generated text, pseudo-writing, watermark, logo, UI, monochrome, torn clothing, modern objects, or fantasy architecture.
```

この固定部を短縮・省略・場面文の後ろへ移動しない。脚本にない雨、火花、青い発光を雰囲気目的で足さない。

**前ページを入れるため見開きは順番に生成する**(前の結果を次の入力にするので並列不可)。同じ部屋が続く場面で背景がブレなくなる。

## ⛔ 絶対ルール(`bible/style/absolute_rules.md` R1〜R7)

見開きプロンプトへ自動注入される。特に見開きで効くのは:
- **R7 同一人物の二重描画禁止** — 参照ボード③のラベル通りに全員を別人として描き分け、各人物は1コマ1回だけ
- **R5 顔をコマ枠で切らない** / **R6 群衆を同じ顔のクローンにしない**
- **R4 文字を描かせない**(台詞・擬音は後で写植)

## 手順(ターミナル / Claude Code)

```bash
# 見開きを順番に生成(参照ボード合成→codex exec→PNG保存→状態記録まで自動)
node pipeline/generate_spread.mjs scripts/v01/ep03_帰ったのに死んだ男.md \
  --outdir production/v01/ep03 [--spreads 1-3] [--force]
```

- 出力: `<outdir>/spreads/sNN.png`(見開き画像)、`<outdir>/spread_boards/sNN_board.png`(参照ボード)、`<outdir>/spread_state.json`(再開点)
- 生成済みの見開きはスキップ(`--force`で再生成)。Codex枠切れ後も再実行で続きから
- `--spreads 2` のように範囲指定可。ただし前ページ連続性を効かせるなら1から順に

## 手順(Codex CLI からそのまま使う)

Codex セッション内では、**別の codex を起動せず**、自分の `image_gen__imagegen` を直接呼ぶのが効率的。`--prepare` で素材と指示文だけ用意する:

```bash
# 参照ボードを合成し、image_gen へ渡す指示文を書き出す(codexは呼ばない)
node pipeline/generate_spread.mjs scripts/v01/ep03_帰ったのに死んだ男.md \
  --outdir production/v01/ep03 --spreads 1 --prepare
```

これで次が生成される:
- `<outdir>/spread_boards/s01_board.png` — 参照ボード1枚
- `<outdir>/spread_boards/s01.instruction.txt` — image_gen へ渡す完全な指示文

Codexエージェントは `s01.instruction.txt` を読み、参照ボード内に承認画風アンカーがあり、prompt冒頭に固定プロンプト契約があることを確認する。欠けていれば生成せずprepare工程を修正する。揃った後は `referenced_image_paths` とpromptを変更せず `image_gen__imagegen` に渡し、指定先へ保存する。前ページ連続性を使うときはs01生成後にs02を `--prepare` する。

Codex 呼び出し規約(プロジェクト CLAUDE.md 準拠):
```bash
codex exec --ephemeral --skip-git-repo-check -C /Users/user/manga/senki \
  -c model_reasoning_effort="low" --color never -o <結果> "<s01.instruction.txt の中身>"
```

## スマホ ChatGPT アプリから使う

同じ参照ボードとプロンプトを GitHub 経由で配る `export_spread_prompts.mjs` がある(`chatgpt_spread_system_prompt.md` 参照)。ボードは GitHub raw URL で渡す。

## 前提と検品

- 登場キャラのシートが registry で整備済みであること(未整備は `manga-bible` で先に生成)
- 生成後は `manga-qa` の観点で見開き画像を検品(R7二重描画・R5顔切れ・R6クローン・人物取り違えを最優先)
- 写植: 見開きは1枚絵なので、`edit_server.mjs` の自由配置(x,y%)で吹き出しを重ねる(個別コマ合成の compose とは別経路)

## 関連ファイル

- `pipeline/reference_board.mjs` — 参照ボード合成(前ページ+画風+人物+小道具→1枚)。`buildReferenceBoard()` を export
- `pipeline/generate_spread.mjs` — 見開き生成ランナー(順次・状態管理・--prepare)
- `pipeline/character_composite.mjs` — 人物のみの名前ラベル合成(1コマ生成 generate_panels 用)

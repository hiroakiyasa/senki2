#!/usr/bin/env node

import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));

const episodes = [
  ['ep01_黒田の前進.md', 169, '黒田の前進'],
  ['ep02_泥の槍衾.md', 170, '泥の槍衾'],
  ['ep03_大橋掃部.md', 171, '大橋掃部'],
  ['ep04_動かぬ西軍.md', 172, '動かぬ西軍'],
  ['ep05_小早川の山.md', 173, '小早川の山'],
  ['ep06_島津の退き口.md', 174, '島津の退き口'],
  ['ep07_勝者の名簿.md', 175, '勝者の名簿'],
  ['ep08_筑前へ.md', 176, '筑前へ'],
];

const expectedPerPage = [1, 3, 7, 3, 3, 3, 7, 3, 2, 7, 3, 1];
const errors = [];
let volumePanels = 0;

function fail(file, message) {
  errors.push(`${file}: ${message}`);
}

for (const [file, serial, title] of episodes) {
  const path = join(here, file);
  if (!existsSync(path)) {
    fail(file, 'file is missing');
    continue;
  }

  const text = readFileSync(path, 'utf8').replace(/\r\n/g, '\n');

  if (!text.includes(`（通算${serial}/240）`)) {
    fail(file, `serial marker ${serial}/240 is missing`);
  }
  if (!text.includes(`「${title}」`)) {
    fail(file, `title ${title} is missing`);
  }
  if (!text.includes('# manga-spread 運用メモ')) {
    fail(file, 'manga-spread operation memo is missing');
  }
  if (!text.includes('終了時の台帳')) {
    fail(file, 'continuity ledger is missing');
  }

  const pageMatches = [...text.matchAll(/^## P(\d+)（[^\n]*$/gm)];
  if (pageMatches.length !== 12) {
    fail(file, `expected 12 page headings, found ${pageMatches.length}`);
  }

  const seenPages = new Set();
  let episodePanels = 0;

  for (let i = 0; i < pageMatches.length; i += 1) {
    const match = pageMatches[i];
    const page = Number(match[1]);
    const start = match.index;
    const end = i + 1 < pageMatches.length ? pageMatches[i + 1].index : text.length;
    const block = text.slice(start, end);
    const panels = [...block.matchAll(/^### c\d+［[^\n]+］$/gm)];

    seenPages.add(page);
    episodePanels += panels.length;

    const expected = expectedPerPage[page - 1];
    if (expected === undefined) {
      fail(file, `unexpected page P${page}`);
    } else if (panels.length !== expected) {
      fail(file, `P${page} expected ${expected} panels, found ${panels.length}`);
    }

    for (let p = 0; p < panels.length; p += 1) {
      const panelStart = panels[p].index;
      const panelEnd = p + 1 < panels.length ? panels[p + 1].index : block.length;
      const panelBlock = block.slice(panelStart, panelEnd);
      const panelName = panels[p][0];

      if (!/^画:/m.test(panelBlock)) {
        fail(file, `P${page} ${panelName} has no 画: field`);
      }
      if (!/^生成:/m.test(panelBlock)) {
        fail(file, `P${page} ${panelName} has no 生成: field`);
      }
    }
  }

  for (let page = 1; page <= 12; page += 1) {
    if (!seenPages.has(page)) fail(file, `P${page} is missing`);
  }

  if (episodePanels !== 43) {
    fail(file, `expected 43 panels, found ${episodePanels}`);
  }
  volumePanels += episodePanels;

  const generationCount = (text.match(/^生成:/gm) ?? []).length;
  if (generationCount !== 43) {
    fail(file, `expected 43 生成 fields, found ${generationCount}`);
  }

  const artCount = (text.match(/^画:/gm) ?? []).length;
  if (artCount < 43) {
    fail(file, `expected at least 43 画 fields, found ${artCount}`);
  }
}

if (volumePanels !== 344) {
  errors.push(`volume: expected 344 panels, found ${volumePanels}`);
}

if (errors.length > 0) {
  console.error('Volume 22 validation failed.');
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log('Volume 22 validation passed.');
console.log(`Episodes: ${episodes.length}`);
console.log(`Pages: ${episodes.length * 12}`);
console.log(`Panels: ${volumePanels}`);
console.log(`Per-page pattern: ${expectedPerPage.join('-')}`);

#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = path.resolve(process.cwd(), 'scripts/v13');
const expected = [
  ['ep097_耳川の記憶.md', 97, '耳川の記憶'],
  ['ep098_肥後の火.md', 98, '肥後の火'],
  ['ep099_島津の釣り.md', 99, '島津の釣り'],
  ['ep100_退路を断つ者.md', 100, '退路を断つ者'],
  ['ep101_豊久の槍.md', 101, '豊久の槍'],
  ['ep102_義弘の決断.md', 102, '義弘の決断'],
  ['ep103_府内の恐怖.md', 103, '府内の恐怖'],
  ['ep104_戸次川へ.md', 104, '戸次川へ'],
];

function fail(message) {
  throw new Error(message);
}

function countMatches(text, regex) {
  return [...text.matchAll(regex)].length;
}

function pagePanelCounts(text) {
  const pageMatches = [...text.matchAll(/^## P(\d+)\b.*$/gm)];
  const counts = [];

  for (let i = 0; i < pageMatches.length; i += 1) {
    const page = Number(pageMatches[i][1]);
    const start = pageMatches[i].index;
    const end = i + 1 < pageMatches.length ? pageMatches[i + 1].index : text.length;
    const section = text.slice(start, end);
    const panels = countMatches(section, /^### c\d+\[/gm);
    counts.push({ page, panels });
  }

  return counts;
}

const results = [];
let hasError = false;

for (const [file, episode, title] of expected) {
  const fullPath = path.join(root, file);
  const errors = [];

  if (!fs.existsSync(fullPath)) {
    results.push({ file, ok: false, errors: ['file not found'] });
    hasError = true;
    continue;
  }

  const text = fs.readFileSync(fullPath, 'utf8');
  const pages = pagePanelCounts(text);
  const pageCount = pages.length;
  const panelCount = pages.reduce((sum, entry) => sum + entry.panels, 0);
  const rapidPages = pages.filter((entry) => entry.panels >= 7).map((entry) => entry.page);
  const lowDensityPages = pages
    .filter((entry) => entry.panels >= 2 && entry.panels <= 3)
    .map((entry) => entry.page);

  if (!text.includes(`v13ep${String(episode).padStart(3, '0')}`)) {
    errors.push(`missing episode id v13ep${String(episode).padStart(3, '0')}`);
  }
  if (!text.includes(`「${title}」`)) {
    errors.push(`missing title ${title}`);
  }
  if (pageCount !== 12) errors.push(`expected 12 pages, got ${pageCount}`);
  if (panelCount !== 43) errors.push(`expected 43 panels, got ${panelCount}`);
  if (rapidPages.length < 2 || rapidPages.length > 3) {
    errors.push(`expected 2-3 rapid pages, got ${rapidPages.length}: ${rapidPages.join(',')}`);
  }
  if (lowDensityPages.length < 4) {
    errors.push(`expected at least 4 pages with 2-3 panels, got ${lowDensityPages.length}`);
  }

  const p1 = pages.find((entry) => entry.page === 1);
  const p12 = pages.find((entry) => entry.page === 12);
  if (!p1 || p1.panels !== 1) errors.push('P1 must be one panel');
  if (!p12 || p12.panels !== 1) errors.push('P12 must be one panel');

  const p1Section = text.match(/^## P1\b[\s\S]*?(?=^## P2\b)/m)?.[0] ?? '';
  const p12Section = text.match(/^## P12\b[\s\S]*?(?=^---$|\Z)/m)?.[0] ?? '';
  if (!p1Section.includes('splash:bleed')) errors.push('P1 missing splash:bleed');
  if (!p12Section.includes('splash:bleed')) errors.push('P12 missing splash:bleed');

  // Three consecutive 4-5 panel pages are forbidden.
  for (let i = 0; i <= pages.length - 3; i += 1) {
    const window = pages.slice(i, i + 3);
    if (window.every((entry) => entry.panels >= 4 && entry.panels <= 5)) {
      errors.push(`forbidden three-page 4-5 panel run at P${window[0].page}-P${window[2].page}`);
    }
  }

  // Visual-continuity reminders. These terms may appear in prohibition notes,
  // so only inspect actual drawing-description lines.
  const drawingLines = text
    .split('\n')
    .filter((line) => line.startsWith('画:'))
    .join('\n');

  if (/黒槍|黒塗りの槍/.test(drawingLines)) {
    errors.push('black spear appears in a drawing description before canon allows it');
  }
  if (/右肩.*(傷|裂|負傷)|肩.*後遺症/.test(drawingLines)) {
    errors.push('future right-shoulder injury appears in a drawing description');
  }
  if (/天守|近代橋|コンクリート/.test(drawingLines)) {
    errors.push('forbidden architecture appears in a drawing description');
  }

  const sfxCount = countMatches(text, /^音「/gm);
  const shoutCount = countMatches(text, /叫び=/g) + countMatches(text, /！/g);
  if (sfxCount < 9) errors.push(`too few explicit SFX entries: ${sfxCount}`);
  if (shoutCount < 3) errors.push(`too few shout indicators: ${shoutCount}`);

  const ok = errors.length === 0;
  if (!ok) hasError = true;
  results.push({
    file,
    ok,
    pageCount,
    panelCount,
    pagePanels: pages.map((entry) => entry.panels),
    rapidPages,
    lowDensityPages,
    sfxCount,
    errors,
  });
}

console.log(JSON.stringify({ ok: !hasError, episodes: results }, null, 2));

if (hasError) process.exitCode = 1;

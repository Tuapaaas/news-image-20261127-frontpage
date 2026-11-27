// news-image-20261127 — "The World in One Day", Friday 27 November 2026.
//
// The entry is a newspaper front page drawn by render.py (Pillow) and
// committed to this repository as entry.png. This program's whole job is
// to place those exact bytes at /output/entry.png: the grader runs it
// twice with no network, and a byte-for-byte copy is deterministic by
// construction, so both runs write the same file.
//
// Output directory: $MAKEFUN_OUTPUT_DIR when the harness sets it,
// otherwise /output, the writable mount the rules promise.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

if (!existsSync(source)) {
  console.error(`entry image missing from repository: ${source}`);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

// The gate reads exactly the bytes in the file, so prove the copy landed
// whole: the target must be the same size as the committed image.
const bytes = statSync(target).size;
if (bytes !== statSync(source).size) {
  console.error(`copy truncated: ${target} is ${bytes} bytes`);
  process.exit(1);
}
console.log(`wrote ${target} (${bytes} bytes)`);

# Output validation

Apply only branches matching the output. Core semantic review in SKILL.md applies to every task; mechanical checks cannot establish semantic completeness.

## Mermaid

Parse/render new or revised diagrams with an available Mermaid-capable viewer. Follow the visual acceptance criteria in [mermaid-style.md](mermaid-style.md); balanced fences alone prove neither grammar nor appearance. Report missing renderer or target-reader checks honestly.

For browser rendering, use `scripts/render_mermaid.cjs` (relative to the skill root) with an available Playwright runtime and local Mermaid browser bundle. It retains screenshots under a content/environment key; `--force` rechecks rendering. Cached rendering success is not automatically visual review and does not prove behavior under every Obsidian theme. Reuse visual review only for unchanged inspected assets.

For a pure split, compare original and destination Mermaid blocks without requiring a style redesign. Exact line/block checks supplement, not replace, semantic review after restructuring.

## Linked notes

Run the read-only validator on the final collection; after repairs recheck impacted content and finish with a full mechanical pass. SCRIPT below is the skill's `scripts/validate_notes.py`:

```sh
python3 SCRIPT --root VAULT_ROOT --index INDEX.md --notes-dir NOTES_DIR --before BACKUP.md
```

Paths may be absolute or relative to `--root`. Use the actual vault root, or the portable output root when no vault exists. Use `--before` for pure splitting where original Mermaid blocks must be retained; omit it for intentional diagram revisions.

The checker covers the index and Markdown under NOTES_DIR, fenced blocks, file targets, reachability, return links and Mermaid block preservation. It excludes directories named `备份`, `backup`, `backups`, and explicit `--exclude` globs from live discovery. A backup link in the index is allowed.

Qualified wiki paths resolve from the root; bare titles resolve only when unique, with ambiguous matches reported as errors. Escaped wiki aliases in Markdown tables are supported. PDF page bounds, including selection/color parameters, require `pypdf`; missing dependencies are errors. Non-PDF heading/block anchors are not validated; same-file anchors are accepted without checking their existence. The validator does not check Mermaid grammar, rendering or semantic completeness.

Exit code 0 means the mechanical check passed; 1 means errors. Use temporary copies to test failures. Never create empty placeholder notes to hide missing sources; repair paths or report unavailable sources.

## Source figures

Apply the figure checks in [obsidian-notes.md](obsidian-notes.md), including reading guidance, source attribution, attachment links and actual embedded appearance where available. Link validation alone does not establish visual correctness. Only byte-unchanged figures can reuse prior visual review; modified crops or exported figures require a new check.

## Full conversion

Use the evidence ledger in [efficient-workflow.md](efficient-workflow.md) to verify every-page text/visual coverage and difficult content. Review original annotations, English statements, qualifiers, calculations, supplemental labels and annotation migration separately from scripts. Run linked-note, Mermaid and source-figure branches when those outputs are present.

For full lecture/session notes, additionally verify:

- The number of page entries equals the PDF page count; page numbers are continuous, unique and in source order across chapters.
- Every page belongs to exactly one primary chapter, including title, agenda, transition and repeated animation pages.
- Every page heading links to the matching PDF page and is immediately followed by exactly one matching complete-slide embed before its explanation.
- Every complete-slide attachment exists in the permanent course attachment directory; its filename page number matches the heading and no final embed points into a cache or temporary directory.
- Complete-slide images preserve the full frame, source aspect ratio, light opaque background, axes, legends, units and necessary context. Supplementary crops are clearly distinguished.
- The session index links directly to chapters and its overview diagram stops at the chapter level. Chapter maps summarize internal knowledge without replacing the page-by-page body.
- Chapter return and previous/next navigation works, and the embedded result is inspected in the target viewer. When dark mode is relevant, confirm actual text and chart contrast rather than assuming the image background is sufficient.

Use a deterministic count/path check where possible, then inspect the images and rendered notes visually. Link existence alone does not prove correct page-image pairing, readability or semantic coverage. Keep full reports locally and return counts, paths and exceptions; read only failing excerpts during correction.

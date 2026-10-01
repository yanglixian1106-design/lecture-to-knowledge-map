# Obsidian linked-note convention

## Organization

Detect the nearest ancestor `.obsidian` directory without changing configuration. If none exists, use the output directory as the portable link root and explain that it should be opened as a vault or migrated with links adjusted. Use course/session filename prefixes, not hard-coded course names or note counts.

Use an existing user-selected structure. Otherwise, for a full lecture/session conversion, create an index and chapter entry notes only: the index owns the course/session overview and stops at chapters, while each chapter owns its chapter map and page-by-page teaching. Create concept notes only when the user requests them or the concept needs an independently reusable canonical home. For a local concept conversion, create concept notes as needed. Cross-concept overview diagrams stay in the chapter entry; common comparison material has one canonical home linked from related concepts.

For a full lecture/session conversion, a typical organization is `course-index.md`, `notes/COURSE-01 Chapter.md`, `图示/逐页课件/`, and `notes/备份/`. A local concept conversion may additionally use `notes/COURSE-Concept.md`. These are patterns, not mandatory filenames. Preserve the original filename as the entry point when splitting an existing document. Save exact original bytes into a unique timestamped backup before replacing that file. Exclude backups from live navigation and validation discovery, except for an explicit backup link in the index.

## Link rules

Prefer `[[vault-relative/path/to/note|Readable Label]]` without `.md`; attachments retain extensions. Paths use `/`, never local absolute paths. Resolve attachments from the original source's location when moving notes, not from the new note directory. Avoid filenames containing `|`, `#`, `[` or `]`.

Each note links directly to the index. In a full lecture/session conversion, the index lists chapters only and chapter notes keep concepts in their body; do not add a concept index unless the user explicitly requests one. If concept notes exist, they also link to their chapter, and chapter entries list them. Add meaningful cross-links rather than a complete graph. Links in both directions are explicit authored navigation; Obsidian additionally derives backlinks.

Use page references such as `[[course/slides.pdf#page=22|课件第22页]]` when useful. Do not invent source page numbers. A section derived only from the user's notes should cite those notes instead. Checker behavior and limitations are centralized in [validation.md](validation.md).

## Note pattern

```markdown
# English Concept（中文名称）

[[course/index|返回总目录]] · 所属章节：[[course/notes/COURSE-Chapter|章节名称]]

来源：[[course/slides.pdf#page=22|课件第22页]]

## 核心概念

State the key definition, theorem or conclusion accurately in English.

用中文解释直觉、意义与易错点；重要辨析先用英文表述。

## 案例与公式

State assumptions in English; retain standard notation and English variable names.

案例保留英文关键措辞，用中文讲解计算。保留来源中的观察窗口，补充推导明确标注。

## 相关笔记

- [[course/notes/COURSE-Related Concept|相关概念]]
```

Include only sections that have actual content. Keep an intact diagram with its explanation, not necessarily in every concept note. Preserve all substantive source material during splitting; a reference link alone is not a substitute for assigning the original content to a destination.

## Full lecture/session chapter pattern

Before drafting, map every PDF page to exactly one primary chapter. Keep the session index compact: its Mermaid overview contains the root and chapter nodes, not all concepts or pages. Chapter maps may summarize their internal concepts, but they never replace the page-by-page explanations.

Within a chapter, keep the source order and use this pattern for every page:

```markdown
## 逐页讲解

### [[course/slides.pdf#page=1|第 1 页]]｜页面主题

![[course/图示/逐页课件/COURSE-slide-p01.png|900]]

用中文详细解释本页的目的、核心内容以及它与前后页面的关系；保留重要 English terms、公式、数字、口径、分母、观察窗口和限制。
```

Use one heading and one complete slide image per source page, including title, agenda, transition and repeated animation pages. Repeated pages can share a concise explanation, but each retains its own heading, image and description of the substantive difference. On chart pages, explain encodings, the analytical question and likely misreadings. On text pages, explain the page's role and knowledge rather than merely transcribing it.

Store complete page images in a dedicated course-local subdirectory such as `图示/逐页课件/`. Use a collision-safe course/session prefix and zero-padded source page, for example `S6-slide-p01.png`. Preserve the source aspect ratio and a light opaque background. Export the complete slide without cropping; a representative crop may be added separately when it improves teaching. A display width near `900` is a starting point for ordinary widescreen slides, not a fixed size: adjust it after checking label readability in the target viewer.

## Embedded course figures

For local concept notes and supplementary teaching figures, choose representative figures for teaching value and place them with their concepts, not in an unrelated gallery. Prefer original course figures. Crops must preserve axes, legends, units and necessary context; use the full slide when a crop cannot retain them. Clearly label redrawn or supplementary illustrations. Add concise reading guidance describing encodings, suitable questions and likely misreadings. Preserve a light, opaque background so source figures remain readable in dark mode. These representative figures supplement, rather than replace, the complete slide images required by a full lecture/session conversion.

Store figures in the course's existing attachment directory, or create a course-local `图示/` directory when none exists. Use collision-safe course/session-prefixed filenames with a descriptive chart name and source page. Embed with vault-relative paths and retain the file extension; do not link to temporary renders outside the portable notes folder.

For example, in a concept note:

```markdown
## 图示对照

![[course/图示/COURSE-grouped-bar-p22.png|700]]

**读图提示：**颜色区分系列，同一类别内的柱子并排排列，适合比较组间数值；系列太多会拥挤。

来源：[[course/slides.pdf#page=22|课件第 22 页]]（原课件图示）。
```

The example width is a starting point, not a required size. Adjust for readable labels and note layout. Keep the source's units, denominators, and time windows clear in the figure or accompanying explanation. Mark redrawn or supplementary figures explicitly rather than presenting them as original slide images.

Before delivery, inspect every final figure for clipped axes, legends, labels, or missing context, and check that its reading guidance matches the image. Verify attachment targets and source page links. Inspect the embedded result in the target viewer when available, including dark-mode contrast when relevant; otherwise state that viewer-level rendering was not verified. Link validation alone does not establish image readability or correct source attribution.

## Validation

Before delivery, apply the linked-note and figure branches of [validation.md](validation.md).

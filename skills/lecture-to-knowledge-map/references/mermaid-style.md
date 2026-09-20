# Mermaid authoring and visual checks

Read before generating or modifying a Mermaid diagram; language and source policies remain in SKILL.md.

## Type and live source

Use `mindmap` for the confirmed radial hierarchy and fenced `flowchart LR` for the compact tree. For compact hierarchy edges use `---` without arrowheads. Use directed flowcharts for sequences, decision logic or explicitly qualified causal hypotheses. Keep the editable source as one live Markdown block, not an SVG plus disconnected hidden source.

The compact style uses thin straight connectors, restrained fills and small corner radii. Avoid thick/tapered or filled branches, decorative curves and excessive whitespace. Soft pink category labels are optional.

## Labels and layout

For bilingual flowchart labels use `n1["抽样分布<br/>Sampling Distribution"]`. This line break worked with native SVG text in the user's observed Obsidian setup with both `htmlLabels` options false; verify in the target renderer rather than enabling HTML merely for line breaks. Chinese stays above the English block even when English needs additional lines.

Starting compact-tree settings: `curve: "linear"`, `nodeSpacing: 8`, `rankSpacing: 22`, `padding: 8`, `diagramPadding: 6`, `useMaxWidth: true`, `fontSize: "13px"`. Start with `flowchart.wrappingWidth: 145` for long English labels, tuning to the reading pane. These are starting values, not universal dimensions; wrappingWidth is a wrapping threshold, not a fixed box width.

Size each node to its text, including mixed Chinese and English. Use the same font for measurement and display, comfortable horizontal padding and enough height for every wrapped line. Do not impose shared fixed widths, truncate translations or shrink text. If expanded nodes make a map unwieldy, split by meaningful subtopic without losing knowledge points.

For plain-text labels in Obsidian, start with `htmlLabels: false` at both top level and inside `flowchart`. Changing only the flowchart option and increasing padding did not fully fix observed clipping; setting both produced complete labels. This is an Obsidian-compatible starting point, not a guarantee for all renderers. If HTML labels are necessary, verify measured bounds separately.

Set `linkStyle default fill:none,stroke:#cc9ca5,stroke-width:1px;`. Use unique classes such as `mapRoot`, `mapBranch` and `mapLeaf`; avoid `root`, which can collide with container styles and produce filled connector wedges.

## Visual acceptance

Check every node for bilingual coverage and consistent terminology. Inspect short and long labels after width changes for visible markup, missing final characters, clipped lines, padding and connector overlap. Connectors remain thin and unfilled, and the diagram fits the reading pane at comfortable text size.

Inspect in the actual target reader where available, including colors and contrast. A standalone browser render does not prove Obsidian display, and an unverified theme configuration is not a proven fix. Do not change application-wide appearance to fix a note. Report unavailable target-reader verification. Validation execution and renderer caching are described in [validation.md](validation.md).

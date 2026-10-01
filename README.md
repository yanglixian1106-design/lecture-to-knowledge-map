# Lecture to Knowledge Map

A Codex skill that turns lecture slides, handouts, and existing study notes into compact Mermaid knowledge maps and linked Obsidian notes.

[English](#english) · [中文](#中文)

## English

### What it does

`lecture-to-knowledge-map` organizes course material into readable, source-traceable study notes.

For a complete lecture or session, the default output is:

```text
Session index
├── Chapter 1
├── Chapter 2
└── Chapter 3
```

The session index stops at the chapter level. Each chapter explains every source page in order:

1. A link to the original PDF page.
2. A complete slide screenshot with a light, opaque background.
3. A detailed Chinese explanation that preserves important English terminology, formulas, numbers, definitions, denominators, observation windows, and qualifications.

Chart pages also explain visual encodings, the analytical question the chart answers, and likely misreadings. Title, agenda, transition, and repeated animation pages are retained so page coverage remains complete.

For focused concept work, the skill can still create reusable concept notes and select representative source figures instead of forcing a full page-by-page conversion.

### Main capabilities

- Build compact Mermaid course and chapter maps.
- Convert complete PDFs into chapter-based, page-by-page Obsidian notes.
- Embed one full-slide image for every source page.
- Preserve formulas, examples, assumptions, annotations, and source page links.
- Use Chinese explanations with accurate English terms and source wording.
- Create vault-relative links and course-local attachment folders.
- Preserve user edits and make collision-safe backups before replacing existing notes.
- Validate links, PDF page bounds, navigation, code fences, page coverage, and slide-image pairing.
- Inspect Mermaid rendering and image readability, including dark-mode contrast when available.

### Installation

Clone the repository and copy the skill directory into your personal Codex skills directory:

```sh
git clone https://github.com/yanglixian1106-design/lecture-to-knowledge-map.git
mkdir -p ~/.codex/skills
cp -R lecture-to-knowledge-map/skills/lecture-to-knowledge-map ~/.codex/skills/
```

The repository also contains `.codex-plugin/plugin.json` for plugin-based installation. This is a Codex skill, not an Obsidian community plugin.

### Example prompts

```text
Use $lecture-to-knowledge-map to turn this PDF into Obsidian notes.
Keep the session index at the chapter level, explain every slide inside its chapter,
and embed a complete screenshot for every page.
```

```text
Use $lecture-to-knowledge-map to reorganize these notes according to the supplied agenda.
Preserve my edits, formulas, examples, and source-page references.
```

```text
Use $lecture-to-knowledge-map to create only one compact Mermaid overview.
Do not split it into multiple notes.
```

### Typical output

```text
Course Vault/
└── Session 6/
    ├── Session-6-知识地图.md
    ├── slides.pdf
    ├── 思维导图/
    │   ├── S6-01 Scope.md
    │   ├── S6-02 Hypothesize.md
    │   ├── S6-03 Validate.md
    │   └── S6-04 Recommend.md
    └── 图示/
        └── 逐页课件/
            ├── S6-slide-p01.png
            ├── S6-slide-p02.png
            └── ...
```

Open the vault root in Obsidian so vault-relative note, PDF, and attachment links resolve correctly. Mermaid diagrams render in Obsidian reading view without requiring a community plugin.

### Validation

Validate generated notes from the repository root:

```sh
python3 skills/lecture-to-knowledge-map/scripts/validate_notes.py \
  --root /path/to/vault \
  --index course/index.md \
  --notes-dir course/notes
```

PDF page-bound validation requires `pypdf`. The skill also requires visual review for Mermaid diagrams and embedded slide images because link validation alone cannot confirm readability, correct page-image pairing, or semantic completeness.

### Repository structure

```text
.codex-plugin/plugin.json
skills/lecture-to-knowledge-map/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── efficient-workflow.md
│   ├── mermaid-style.md
│   ├── obsidian-notes.md
│   └── validation.md
└── scripts/
    ├── lecture_pipeline.py
    ├── render_mermaid.cjs
    ├── validate_notes.py
    └── tests/test_pipeline.py
```

The repository contains the reusable skill, references, and validation helpers. It does not contain course PDFs or personal notes.

---

## 中文

### 功能说明

`lecture-to-knowledge-map` 用于把课程课件、讲义和已有学习笔记整理为结构清晰、来源可追溯的 Mermaid 知识地图与 Obsidian 笔记。

整理完整 Lecture 或 Session 时，默认采用两级结构：

```text
Session 总目录
├── 第 1 章
├── 第 2 章
└── 第 3 章
```

Session 首页只展开到章节。每个章节按照课件原始顺序逐页讲解：

1. 链接到原 PDF 页码。
2. 插入保留浅色不透明背景的完整课件截图。
3. 使用中文详细解释，同时保留重要英文术语、公式、数字、指标定义、分母、观察窗口和限制条件。

图表页面还会解释视觉编码、图表适合回答的问题和容易误读之处。封面、议程、过渡页和重复动画页同样保留，确保课件页面没有遗漏。

如果任务只针对某个概念，技能仍可按需创建独立概念笔记并选择代表图示，不会强制执行完整逐页转换。

### 主要能力

- 生成紧凑的课程与章节 Mermaid 导图。
- 将完整 PDF 整理为以章节为单位的逐页 Obsidian 笔记。
- 为每一页课件嵌入一张完整截图。
- 保留公式、案例、假设、批注和来源页码。
- 使用中文讲解并保留准确的英文术语与原课件措辞。
- 使用 Vault 相对链接和课程本地附件目录。
- 修改已有笔记前保护用户内容并建立不会覆盖旧文件的备份。
- 检查链接、PDF 页码、导航、代码围栏、页面覆盖和截图对应关系。
- 在条件允许时检查 Mermaid 实际渲染、图片清晰度和深色模式对比度。

### 安装

克隆仓库，并把技能目录复制到个人 Codex skills 目录：

```sh
git clone https://github.com/yanglixian1106-design/lecture-to-knowledge-map.git
mkdir -p ~/.codex/skills
cp -R lecture-to-knowledge-map/skills/lecture-to-knowledge-map ~/.codex/skills/
```

仓库同时包含 `.codex-plugin/plugin.json`，可用于插件形式的安装。本项目是 Codex skill，不是 Obsidian 社区插件。

### 使用示例

```text
使用 $lecture-to-knowledge-map，把这份 PDF 整理成 Obsidian 笔记。
Session 首页只保留章节层级，在章节内逐页详细讲解，并给每一页插入完整课件截图。
```

```text
使用 $lecture-to-knowledge-map，按照我提供的大纲重新组织这些笔记。
保留我的修改、公式、案例和来源页码。
```

```text
使用 $lecture-to-knowledge-map，只生成一份紧凑的 Mermaid 总导图，不拆分笔记。
```

### 典型输出结构

```text
课程 Vault/
└── Session 6/
    ├── Session-6-知识地图.md
    ├── slides.pdf
    ├── 思维导图/
    │   ├── S6-01 Scope.md
    │   ├── S6-02 Hypothesize.md
    │   ├── S6-03 Validate.md
    │   └── S6-04 Recommend.md
    └── 图示/
        └── 逐页课件/
            ├── S6-slide-p01.png
            ├── S6-slide-p02.png
            └── ...
```

应在 Obsidian 中打开 Vault 根目录，确保笔记、PDF 和附件的相对链接能够正确解析。Obsidian 阅读视图可以直接渲染 Mermaid，无需额外安装社区插件。

### 校验

在仓库根目录运行：

```sh
python3 skills/lecture-to-knowledge-map/scripts/validate_notes.py \
  --root /path/to/vault \
  --index course/index.md \
  --notes-dir course/notes
```

检查 PDF 页码范围需要安装 `pypdf`。此外仍需目视检查 Mermaid 和课件截图，因为链接存在并不能证明图片清晰、页码与截图匹配或讲解内容完整。

### 仓库结构

```text
.codex-plugin/plugin.json
skills/lecture-to-knowledge-map/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── efficient-workflow.md
│   ├── mermaid-style.md
│   ├── obsidian-notes.md
│   └── validation.md
└── scripts/
    ├── lecture_pipeline.py
    ├── render_mermaid.cjs
    ├── validate_notes.py
    └── tests/test_pipeline.py
```

仓库只包含可复用的技能、参考规范和校验工具，不包含课程 PDF 或个人笔记。

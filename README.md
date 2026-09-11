# Lecture to Knowledge Map

将课件、讲义和学习笔记转换为 **Mermaid 分层思维导图**与 **Obsidian 互链概念笔记**的 Codex skill，附 Codex 插件清单。

默认使用中文解释，保留英文关键概念。支持新建知识图谱、按指定大纲调整层级，以及将已有笔记拆分成互链笔记。

## 功能

- 按课程 → 章节 → 概念组织知识，保留案例、公式、假设和来源页码。
- 使用 Mermaid mindmap 表达层级，flowchart 表达顺序或决策逻辑。
- 生成总目录、章节与概念笔记，提供返回链接和相关概念链接。
- 拆分已有笔记前保留完整备份；将课程图示放在对应概念旁。
- 提供只读校验脚本，检查链接目标、目录可达性、返回链接与代码围栏。

## 安装为个人 skill

克隆仓库后，将 `skills/lecture-to-knowledge-map` 文件夹复制到 `~/.codex/skills/`。如果已有同名 skill，请先备份并比较内容，再决定是否替换。安装后在新任务中使用。

```sh
git clone https://github.com/yanglixian1106-design/lecture-to-knowledge-map.git
```

仓库根目录的 `.codex-plugin/plugin.json` 提供插件元数据，`skills/` 包含完整 skill。此仓库不包含 marketplace 配置。

## 使用示例

向 Codex 提供课件或笔记，然后输入：

> 使用 $lecture-to-knowledge-map，把这份课件整理为分层思维导图，保留来源页码。

> 按我提供的课程大纲调整知识层级，保留原有公式与案例。

> 将这份笔记拆分成 Obsidian 总目录、章节和概念笔记，保留原文件备份并校验链接。

只需要导图时，明确说明“只生成一份 Markdown 导图，不拆分笔记”。

## 校验生成的笔记

需要 Python 3.9 或更高版本；脚本仅使用标准库。从仓库根目录运行：

```sh
python3 skills/lecture-to-knowledge-map/scripts/validate_notes.py \
  --root /path/to/vault \
  --index course/index.md \
  --notes-dir course/notes
```

纯拆分且需要保留原 Mermaid 图时，加上 `--before course/backup.md`。路径相对于 `--root`，也可使用绝对路径。

校验不覆盖标题锚点、Mermaid 语法与实际渲染、公式正确性或语义完整性。PDF/PPT 内容读取及图片渲染需要运行环境提供相应工具；本插件不捆绑 OCR 或 PDF/PPT 引擎。

## 文件结构

```text
.codex-plugin/plugin.json
skills/lecture-to-knowledge-map/
├── SKILL.md
├── agents/openai.yaml
├── references/obsidian-notes.md
└── scripts/validate_notes.py
```

本仓库仅包含可复用的 skill、参考规范和校验脚本，不包含课程资料或个人笔记。

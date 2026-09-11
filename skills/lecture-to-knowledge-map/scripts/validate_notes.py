#!/usr/bin/env python3
"""Read-only validation of a scoped Obsidian note collection (stdlib only)."""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys


def scan(text):
    """Return prose, Mermaid bodies and fence errors; support backticks/tilde fences."""
    prose, diagrams, errors = [], [], []
    fence = None
    body = []
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            char, length, language, start = fence
            if re.fullmatch(r' {0,3}' + re.escape(char) + '{' + str(length) + r',}\s*', line):
                if language == 'mermaid':
                    diagrams.append('\n'.join(body).strip())
                fence = None
                body = []
            else:
                body.append(line)
        else:
            match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
            if match:
                delimiter, info = match.groups()
                fence = (delimiter[0], len(delimiter), info.strip().split()[0] if info.strip() else '', number)
            else:
                prose.append(line)
    if fence:
        errors.append(f'unclosed fence at line {fence[3]}')
    return '\n'.join(prose), diagrams, errors


def validate(root, index, notes_dir, before=None, excludes=()):
    errors = []
    if not root.is_dir() or not notes_dir.is_dir() or not index.is_file():
        return ['root/notes directory or index does not exist'], 0
    ignored = {'备份', 'backup', 'backups'}
    notes = sorted(p.resolve() for p in notes_dir.rglob('*.md')
                   if not ignored.intersection(x.lower() for x in p.relative_to(notes_dir).parts)
                   and not any(p.relative_to(notes_dir).match(g) for g in excludes))
    files = sorted(set(notes + [index]))
    inventory = [p.resolve() for p in root.rglob('*') if p.is_file() and '.obsidian' not in p.parts]
    by_name = {}
    for p in inventory:
        for name in {p.name, p.stem if p.suffix.lower() == '.md' else p.name}:
            by_name.setdefault(name, set()).add(p)

    def resolve(raw, origin):
        target = raw.split('|', 1)[0].split('#', 1)[0].strip()
        if not target:
            return origin
        if Path(target).is_absolute():
            raise ValueError('absolute wiki path: ' + target)
        direct = (root / target).resolve()
        if not direct.is_relative_to(root):
            raise ValueError('wiki path outside vault: ' + target)
        candidates = [direct, Path(str(direct) + '.md')]
        if target.startswith(('./', '../')):
            local = (origin.parent / target).resolve()
            candidates = [local, Path(str(local) + '.md')]
        for candidate in candidates:
            if candidate.is_relative_to(root) and candidate.is_file():
                return candidate
        matches = by_name.get(target, set()) if '/' not in target else set()
        if len(matches) == 1:
            return next(iter(matches))
        if len(matches) > 1:
            raise ValueError('ambiguous wiki target: ' + target)
        raise ValueError('missing wiki target: ' + target)

    graph, diagrams = {}, Counter()
    for p in files:
        prose, blocks, problems = scan(p.read_text(encoding='utf-8'))
        errors.extend(f'{p.name}: {problem}' for problem in problems)
        diagrams.update(blocks)
        graph[p] = set()
        # Ignore inline code examples as well as fenced examples.
        prose = re.sub(r'(`+).*?\1', '', prose)
        for raw in re.findall(r'\[\[([^\]\n]+)\]\]', prose):
            try:
                graph[p].add(resolve(raw, p))
            except ValueError as exc:
                errors.append(f'{p.name}: {exc}')
        if p != index and index not in graph[p]:
            errors.append(f'{p.name}: missing direct return link to index')
    visited, queue = set(), [index]
    while queue:
        p = queue.pop()
        if p not in visited:
            visited.add(p)
            queue.extend(graph.get(p, ()))
    errors.extend(f'{p.name}: unreachable from index' for p in files if p not in visited)
    if before:
        _, old, problems = scan(before.read_text(encoding='utf-8'))
        errors.extend(f'baseline: {x}' for x in problems)
        missing = Counter(old) - diagrams
        if missing:
            errors.append(f'missing Mermaid diagrams from baseline: {sum(missing.values())}')
    return errors, len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--index', required=True, type=Path)
    parser.add_argument('--notes-dir', required=True, type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--exclude', action='append', default=[], help='Glob relative to notes-dir; repeatable')
    args = parser.parse_args()
    root = args.root.resolve()
    def rooted(p):
        return (p if p.is_absolute() else root / p).resolve() if p is not None else None
    try:
        errors, count = validate(root, rooted(args.index), rooted(args.notes_dir), rooted(args.before), args.exclude)
    except (OSError, UnicodeError) as exc:
        errors, count = [str(exc)], 0
    for error in errors:
        print('ERROR:', error, file=sys.stderr)
    if errors:
        print(f'FAIL: {len(errors)} issue(s), {count} notes checked', file=sys.stderr)
        return 1
    print(f'PASS: {count} notes; targets, navigation, fences and requested diagram preservation checked.')
    print('Not checked: anchor existence, Mermaid grammar/rendering, semantic completeness.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

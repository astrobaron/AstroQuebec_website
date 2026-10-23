"""Import bilingual co-investigator expertise without replacing profile metadata.

Usage: python3 scripts/import_expertise.py [workbook.xlsx] [--check]
Uses Python's standard library only. Re-running replaces only the managed
research section and interests. Missing profiles or translations abort all writes.
"""

import argparse
import json
import re
from pathlib import Path
import zipfile

from import_cochercheurs import slugify
from inspect_xlsx import load_shared_strings, rows_from_sheet, sheet_paths

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- imported-expertise:start -->'
END = '<!-- imported-expertise:end -->'


def prepare(workbook, authors):
    with zipfile.ZipFile(workbook) as archive:
        rows = rows_from_sheet(archive, sheet_paths(archive)[0][1],
                               load_shared_strings(archive), limit=100000)
    header = next(i for i, row in enumerate(rows) if 'Keywords' in row)
    columns = rows[header]
    fields = {
        'fr': (columns.index('Champs de recherche (mots clés)'),
               columns.index('Description du projet de recherche')),
        'en': (columns.index('Keywords'), columns.index('Research project description')),
    }
    changes = {}
    seen = set()
    for row in rows[header + 1:]:
        if not any(row):
            continue
        row += [''] * (len(columns) - len(row))
        slug = slugify(f'{row[1]}-{row[0]}')
        if not row[0] or not row[1] or slug in seen:
            raise ValueError(f'Missing or duplicate name: {row[:2]}')
        seen.add(slug)
        for language, (keyword_col, description_col) in fields.items():
            keywords = row[keyword_col].strip()
            description = row[description_col].strip()
            if not keywords or not description:
                raise ValueError(f'Missing {language} expertise for {slug}')
            suffix = '.en' if language == 'en' else ''
            path = authors / slug / f'_index{suffix}.md'
            original = path.read_text(encoding='utf-8')
            front, body = original.split('---', 2)[1:]
            if 'role: "Co-Investigator"' not in front and 'role: "Cochercheur ou cochercheuse"' not in front:
                raise ValueError(f'Not a co-investigator: {path}')
            keywords = re.sub(r'\bCenter\b', 'Centre', keywords)
            keywords = re.sub(r'\bcenter\b', 'centre', keywords)
            description = re.sub(r'\bCenter\b', 'Centre', description)
            description = re.sub(r'\bcenter\b', 'centre', description)
            interests = [part.strip().rstrip('.') for part in re.split(r'[,;\n]+', keywords) if part.strip()]
            front, count = re.subn(r'^interests:.*(?:\n[ \t]+-.*)*',
                                  lambda _: 'interests: ' + json.dumps(interests, ensure_ascii=False),
                                  front, count=1, flags=re.M)
            if count != 1:
                raise ValueError(f'Missing interests field: {path}')
            if body.count(START) != body.count(END) or body.count(START) > 1:
                raise ValueError(f'Invalid managed section: {path}')
            heading = 'Research project' if language == 'en' else 'Projet de recherche'
            section = f'{START}\n\n## {heading}\n\n{description}\n\n{END}'
            if START in body:
                body = re.sub(re.escape(START) + r'.*?' + re.escape(END),
                              lambda _: section, body, flags=re.S)
            else:
                body = body.rstrip() + '\n\n' + section + '\n'
            changes[path] = '---' + front + '---' + body
    if not seen:
        raise ValueError('No expertise records found')
    return changes, len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook', nargs='?', type=Path,
                        default=ROOT / 'exports/co-chercheurs_expertise.xlsx')
    parser.add_argument('--check', action='store_true', help='Validate and report without writing')
    args = parser.parse_args()
    changes, count = prepare(args.workbook, ROOT / 'content/authors')
    changed = sum(path.read_text(encoding='utf-8') != text for path, text in changes.items())
    if not args.check:
        for path, text in changes.items():
            if path.read_text(encoding='utf-8') != text:
                path.write_text(text, encoding='utf-8')
    print(f'{count} co-investigators validated; {changed} profile files ' +
          ('would change' if args.check else 'updated'))


if __name__ == '__main__':
    main()

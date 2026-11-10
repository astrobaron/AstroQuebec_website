"""Generate directory icon data from members_data/axes.xlsx.

Run again after updating the workbook. Profile content is left untouched.
"""

import json
from pathlib import Path
import zipfile

from export_students_list import load_shared_strings, rows_from_sheet, sheet_paths
from import_cochercheurs import read_records, slugify

ROOT = Path(__file__).resolve().parents[1]
AXES = [
    ("axe1_1", "Origine et structure à grande échelle de l’Univers", "Origin and large-scale structure of the Universe"),
    ("axe1_2", "Formation et évolution des galaxies", "Galaxy formation and evolution"),
    ("axe1_3", "Cycle de vie des étoiles", "Stellar life cycles"),
    ("axe1_4", "Systèmes planétaires et origine de la vie", "Planetary systems and the origin of life"),
    ("axe2", "Développement d’instrumentation", "Instrumentation development"),
    ("axe3", "Apprentissage automatique et outils numériques", "Machine learning and numerical tools"),
]


def prepare():
    members = {}
    for record in read_records(ROOT / "members_data/cochercheurs.xlsx"):
        key = slugify(record["last_name"])
        if key in members:
            raise ValueError(f"Ambiguous surname: {key}")
        members[key] = slugify(f"{record['first_name']} {record['last_name']}")
    # The axes workbook omits the second 'h' in Ravanbakhsh.
    aliases = {"ravanbaksh": "ravanbakhsh"}
    with zipfile.ZipFile(ROOT / "members_data/axes.xlsx") as archive:
        rows = rows_from_sheet(archive, sheet_paths(archive)[0][1], load_shared_strings(archive))
    result = {}
    for row in rows[1:]:
        if not any(row):
            continue
        key = slugify(row[0])
        slug = members[aliases.get(key, key)]
        if slug in result:
            raise ValueError(f"Duplicate researcher: {slug}")
        values = row[1:] + [""] * (7 - len(row))
        selected = []
        for index, (axis, _, _) in enumerate(AXES):
            value = values[index].strip().lower()
            allowed = {"", "x"} if index < 4 else {"", "0", "1", "2"}
            if value not in allowed:
                raise ValueError(f"Unexpected value {value!r} for {slug}, {axis}")
            if value not in {"", "0"}:
                selected.append(axis)
        result[slug] = selected
    if set(result) != set(members.values()):
        raise ValueError("The axes workbook does not cover every co-investigator")
    return {
        "axes": {axis: {"fr": fr, "en": en} for axis, fr, en in AXES},
        "members": result,
    }


if __name__ == "__main__":
    data = prepare()
    (ROOT / "data/research_axes.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Updated research axes for {len(data['members'])} co-investigators")

import argparse
import json
import re
import unicodedata
import zipfile
from pathlib import Path

from export_students_list import (
    clean,
    column_map,
    excel_date,
    load_shared_strings,
    normalize,
    rows_from_sheet,
    sheet_paths,
)

GENERATED_MARKER = "generated_by: scripts/import_students.py"

FIELD_ALIASES = {
    "last_name": ["nom / last name", "nom"],
    "first_name": ["prénom / first name", "prenom / first name", "prénom", "prenom"],
    "program": [
        "cycle d'études / graduate studies program",
        "cycle d'etudes / graduate studies program",
        "cycle d'études",
        "cycle d'etudes",
    ],
    "email": ["courriel / email", "courriel", "email"],
    "start_date": [
        "date de début du diplôme / start date of the degree programme",
        "date de debut du diplome / start date of the degree programme",
        "date de début du diplôme",
        "date de debut du diplome",
    ],
    "institution": [
        "établissement d'affiliation / affiliated institution",
        "etablissement d'affiliation / affiliated institution",
        "établissement d'affiliation",
        "etablissement d'affiliation",
    ],
    "director_last_name": ["directeur - nom / director - last name", "directeur - nom"],
    "director_first_name": [
        "directeur - prénom / director - first name",
        "directeur - prenom / director - first name",
        "directeur - prénom",
        "directeur - prenom",
    ],
    "codirector_last_name": [
        "codirecteur1 - nom / co-director1 - last name",
        "codirecteur1 -  nom / co-director1 -  last name",
        "codirecteur1 - nom",
        "codirecteur1 -  nom",
    ],
    "codirector_first_name": [
        "codirecteur1 - prénom / co-director1 - first name",
        "codirecteur1 - prenom / co-director1 - first name",
        "codirecteur1 - prénom",
        "codirecteur1 - prenom",
    ],
    "in_progress": ["en cours / in progress", "en cours"],
}

PROGRAM_ROLES_FR = {
    "2e cycle d'études": "Étudiante ou étudiant à la maîtrise",
    "3e cycle d'études": "Étudiante ou étudiant au doctorat",
    "stage postdoctoral (après un ph.d.)": "Stage postdoctoral",
}

PROGRAM_ROLES_EN = {
    "2e cycle d'études": "Master's Student",
    "3e cycle d'études": "PhD Student",
    "stage postdoctoral (après un ph.d.)": "Postdoctoral Fellow",
}

PROGRAM_GROUPS_FR = {
    "2e cycle d'études": "Étudiantes et étudiants à la maîtrise",
    "3e cycle d'études": "Étudiantes et étudiants au doctorat",
    "stage postdoctoral (après un ph.d.)": "Stagiaires postdoctoraux",
}

PROGRAM_GROUPS_EN = {
    "2e cycle d'études": "Master’s Students",
    "3e cycle d'études": "PhD Students",
    "stage postdoctoral (après un ph.d.)": "Postdoctoral Fellows",
}


def field_column_map(headers):
    normalized = {normalize(header): idx for idx, header in enumerate(headers)}
    mapping = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            idx = normalized.get(normalize(alias))
            if idx is not None:
                mapping[field] = idx
                break
    return mapping


def read_student_records(workbook_path, active_only=True):
    records = []
    seen = set()
    with zipfile.ZipFile(workbook_path) as zf:
        shared_strings = load_shared_strings(zf)
        for sheet_name, sheet_path in sheet_paths(zf):
            rows = rows_from_sheet(zf, sheet_path, shared_strings)
            if not rows or sheet_name.lower().startswith("feuil"):
                continue
            mapping = field_column_map(rows[0])
            if not {"first_name", "last_name"}.issubset(mapping):
                continue
            for row in rows[1:]:
                record = {}
                for field in FIELD_ALIASES:
                    idx = mapping.get(field)
                    value = row[idx] if idx is not None and idx < len(row) else ""
                    record[field] = clean(value, is_date=field == "start_date")
                if not record["first_name"] or not record["last_name"]:
                    continue
                if active_only and record.get("in_progress", "").lower() not in {"x", "yes", "oui", "true", "1"}:
                    continue
                key = (
                    record["first_name"].lower(),
                    record["last_name"].lower(),
                    record["program"].lower(),
                    record["start_date"],
                    record["institution"].lower(),
                )
                if key in seen:
                    continue
                seen.add(key)
                records.append(record)
    records.sort(key=lambda item: (item["last_name"].lower(), item["first_name"].lower(), item["start_date"]))
    return records


def slugify(value):
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "student"


def unique_slug(record, used_slugs, authors_dir):
    base = slugify(f"{record['first_name']} {record['last_name']}")
    candidates = [base]
    if record["program"]:
        candidates.append(f"{base}-{slugify(record['program'])}")
    if record["institution"]:
        candidates.append(f"{base}-{slugify(record['institution'])}")
    if record["start_date"]:
        candidates.append(f"{base}-{slugify(record['start_date'])}")

    for candidate in candidates:
        if candidate in used_slugs:
            continue
        existing = authors_dir / candidate
        if not existing.exists() or is_generated_profile(existing):
            used_slugs.add(candidate)
            return candidate

    index = 2
    while True:
        candidate = f"{base}-{index}"
        if candidate not in used_slugs:
            existing = authors_dir / candidate
            if not existing.exists() or is_generated_profile(existing):
                used_slugs.add(candidate)
                return candidate
        index += 1


def is_generated_profile(author_dir):
    profile = author_dir / "_index.md"
    if not profile.exists():
        return False
    return GENERATED_MARKER in profile.read_text(encoding="utf-8")


def q(value):
    return json.dumps(value, ensure_ascii=False)


def yaml_list(values, indent=2):
    if not values:
        return "[]"
    pad = " " * indent
    return "\n".join(f"{pad}- {q(value)}" for value in values if value)


def role_for(record, lang):
    program_key = record["program"].lower()
    roles = PROGRAM_ROLES_EN if lang == "en" else PROGRAM_ROLES_FR
    return roles.get(program_key, record["program"] or ("Student" if lang == "en" else "Étudiante ou étudiant"))


def group_for(record, lang):
    program_key = record["program"].lower()
    groups = PROGRAM_GROUPS_EN if lang == "en" else PROGRAM_GROUPS_FR
    return groups.get(program_key, "Students" if lang == "en" else "Étudiantes et étudiants")


def director_line(record, lang):
    director = " ".join(part for part in [record["director_first_name"], record["director_last_name"]] if part)
    codirector = " ".join(part for part in [record["codirector_first_name"], record["codirector_last_name"]] if part)
    lines = []
    if director:
        label = "Director" if lang == "en" else "Direction"
        lines.append(f"- **{label}:** {director}")
    if codirector:
        label = "Co-director" if lang == "en" else "Codirection"
        lines.append(f"- **{label}:** {codirector}")
    return "\n".join(lines)


def profile_text(record, slug, lang):
    title = f"{record['first_name']} {record['last_name']}"
    role = role_for(record, lang)
    institution = record["institution"] or "AstroQuébec"
    email = record["email"]
    group = group_for(record, lang)
    generated_note = "Generated from the student spreadsheet." if lang == "en" else "Généré à partir du fichier étudiant."
    program_label = "Graduate studies program" if lang == "en" else "Cycle d'études"
    start_label = "Start date" if lang == "en" else "Date de début"
    social = ""
    if email:
        social = f"""social:
  - icon: envelope
    icon_pack: fas
    link: {q(f"mailto:{email}")}"""
    else:
        social = "social: []"

    details = [
        f"- **{program_label}:** {record['program']}" if record["program"] else "",
        f"- **{start_label}:** {record['start_date']}" if record["start_date"] else "",
        director_line(record, lang),
    ]
    body_details = "\n".join(item for item in details if item)

    return f"""---
{GENERATED_MARKER}
title: {q(title)}
first_name: {q(record["first_name"])}
last_name: {q(record["last_name"])}
authors:
  - {q(slug)}
superuser: false
role: {q(role)}
organizations:
  - name: {q(institution)}
    url: ""
bio: {q(generated_note)}
interests: []
{social}
email: {q(email)}
user_groups:
  - {q(group)}
---

{body_details}
"""


def write_profiles(records, authors_dir, dry_run=False):
    authors_dir.mkdir(parents=True, exist_ok=True)
    used_slugs = set()
    actions = []
    for record in records:
        slug = unique_slug(record, used_slugs, authors_dir)
        author_dir = authors_dir / slug
        action = "update" if author_dir.exists() else "create"
        actions.append((action, slug))
        if dry_run:
            continue
        author_dir.mkdir(parents=True, exist_ok=True)
        (author_dir / "_index.md").write_text(profile_text(record, slug, "fr"), encoding="utf-8")
        (author_dir / "_index.en.md").write_text(profile_text(record, slug, "en"), encoding="utf-8")
    return actions


def prune_generated_profiles(active_slugs, authors_dir, dry_run=False):
    removed = []
    for author_dir in authors_dir.iterdir():
        if not author_dir.is_dir() or author_dir.name in active_slugs or not is_generated_profile(author_dir):
            continue
        files = {path.name for path in author_dir.iterdir() if path.is_file()}
        allowed_files = {"_index.md", "_index.en.md"}
        if not files.issubset(allowed_files):
            raise RuntimeError(f"Refusing to remove generated profile with extra files: {author_dir}")
        removed.append(author_dir.name)
        if not dry_run:
            for filename in allowed_files:
                profile = author_dir / filename
                if profile.exists():
                    profile.unlink()
            author_dir.rmdir()
    return removed


def main():
    parser = argparse.ArgumentParser(description="Create or update Hugo author profiles from a student workbook.")
    parser.add_argument("workbook", nargs="?", default="student_data/students_hugo.xlsx")
    parser.add_argument("--authors-dir", default="content/authors")
    parser.add_argument("--all", action="store_true", help="Import all records, not just rows marked En cours / In progress.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created or updated without writing files.")
    parser.add_argument("--prune", action="store_true", help="Remove generated profiles absent from the imported records.")
    args = parser.parse_args()

    records = read_student_records(Path(args.workbook), active_only=not args.all)
    actions = write_profiles(records, Path(args.authors_dir), dry_run=args.dry_run)
    active_slugs = {slug for _, slug in actions}
    removed = prune_generated_profiles(active_slugs, Path(args.authors_dir), dry_run=args.dry_run) if args.prune else []
    creates = sum(1 for action, _ in actions if action == "create")
    updates = sum(1 for action, _ in actions if action == "update")
    mode = "dry run" if args.dry_run else "written"
    print(f"{mode}: {len(records)} records, {creates} creates, {updates} updates, {len(removed)} removals")
    for action, slug in actions[:20]:
        print(f"{action}: {slug}")
    if len(actions) > 20:
        print(f"... {len(actions) - 20} more")
    for slug in removed:
        print(f"remove: {slug}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import csv
import io
import re
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

GENERATED_MARKER = "generated_by: scripts/import_seminars.py"
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs/export?format=csv&gid=0"
DEFAULT_LOCATION = "Bell Room (Room 103) in the Rutherford building (3600 University) of McGill University"


def normalize_space(value):
    return re.sub(r"\s+", " ", (value or "")).strip()


def slugify(value):
    value = unicodedata.normalize("NFKD", (value or "")).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "seminaire"


def parse_date(value):
    value = normalize_space(value)
    if not value:
        return None
    for fmt in ("%d-%b-%Y", "%d-%b-%y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def is_placeholder_event(value):
    text = normalize_space(value or "").lower()
    if not text:
        return True
    placeholders = [
        "no seminar",
        "no seminar - winter break",
        "winter break",
        "vacances",
        "break",
        "no event",
        "no talk",
    ]
    for placeholder in placeholders:
        if placeholder in text:
            return True
    return False


def parse_row(row):
    speaker = normalize_space(row.get("Speaker") or row.get("speaker") or "")
    raw_date = normalize_space(row.get("Date") or row.get("date") or "")
    title = normalize_space(row.get("Title") or row.get("title") or "")
    abstract = normalize_space(row.get("Abstract") or row.get("abstract") or "")
    affiliation = normalize_space(row.get("Affiliation") or row.get("affiliation") or "")
    host = normalize_space(row.get("Host") or row.get("host") or "")
    zoom = normalize_space(row.get("Zoom Link") or row.get("zoom_link") or row.get("Zoom") or "")

    if is_placeholder_event(speaker) or is_placeholder_event(raw_date) or is_placeholder_event(title):
        return None
    if not raw_date or not speaker:
        return None
    if title.lower() in {"n/a", "na", "none", ""}:
        title = "Titre à confirmer" if True else "Title to be confirmed"
    if abstract.lower() in {"n/a", "na", "none", ""}:
        abstract = "Résumé à confirmer."
    if not title:
        title = f"Séminaire — {speaker}"

    parsed_date = parse_date(raw_date)
    if not parsed_date:
        return None

    local_tz = ZoneInfo("America/Montreal")
    start_dt = parsed_date.replace(hour=13, minute=0, second=0, tzinfo=local_tz)
    end_dt = start_dt + timedelta(hours=2)

    return {
        "speaker": speaker,
        "date": parsed_date,
        "title": title,
        "abstract": abstract,
        "affiliation": affiliation,
        "host": host,
        "zoom": zoom,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "slug": slugify(f"{speaker} {parsed_date.strftime('%Y-%m-%d')}"),
    }


def yaml_quote(value):
    return '"' + str(value).replace('"', '\\"') + '"'


def markdown_details(record, language='fr'):
    label_date = "Date" if language == 'en' else "Date"
    label_time = "Time" if language == 'en' else "Heure"
    label_room = "Location" if language == 'en' else "Lieu"
    label_presenter = "Presenter" if language == 'en' else "Personne présentatrice"
    label_affiliation = "Institution" if language == 'en' else "Institution"
    lines = [
        f"- **{label_date}:** {record['date'].strftime('%d %B %Y' if language == 'fr' else '%B %d, %Y') }",
        f"- **{label_time}:** {record['start_dt'].strftime('%H h') if language == 'fr' else record['start_dt'].strftime('%I:%M %p').replace('AM', 'a.m.').replace('PM', 'p.m.') } à {record['end_dt'].strftime('%H h') if language == 'fr' else record['end_dt'].strftime('%I:%M %p').replace('AM', 'a.m.').replace('PM', 'p.m.') }",
        f"- **{label_room}:** {DEFAULT_LOCATION}",
        f"- **{label_presenter}:** {record['speaker']}",
        f"- **{label_affiliation}:** {record['affiliation'] or ('University / Institution' if language == 'en' else 'Université / institution')}",
    ]
    return "\n".join(lines)


def event_frontmatter(record, language='fr'):
    if language == 'fr':
        title = f"Séminaire — {record['speaker']}"
        event_type = "Colloques et séminaires"
        summary = record['title']
        author_section = "## Détails\n\n"
        title_section = "## Titre\n\n"
        abstract_title = "## Résumé\n\n"
    else:
        title = f"Seminar — {record['speaker']}"
        event_type = "Colloquia and Seminars"
        summary = record['title']
        author_section = "## Details\n\n"
        title_section = "## Title\n\n"
        abstract_title = "## Abstract\n\n"

    body = (
        "---\n"
        f"{GENERATED_MARKER}\n"
        f"title: {yaml_quote(title)}\n"
        f"event: {yaml_quote(event_type)}\n"
        f"summary: {yaml_quote(summary)}\n"
        f"abstract: >-\n  {record['abstract']}\n"
        f"date: \"{record['start_dt'].isoformat()}\"\n"
        f"date_end: \"{record['end_dt'].isoformat()}\"\n"
        "all_day: false\n"
        f"location: {yaml_quote(DEFAULT_LOCATION)}\n"
        "authors: []\n"
        "draft: false\n"
        "profile: false\n"
        "share: false\n"
        "featured: false\n"
        "---\n\n"
        f"{author_section}{markdown_details(record, language=language)}\n\n"
        f"{title_section}{record['title']}\n\n"
        f"{abstract_title}{record['abstract']}\n"
    )
    return body


def ensure_directory(path):
    path.mkdir(parents=True, exist_ok=True)


def fetch_rows(url):
    with urlopen(url, timeout=30) as response:
        raw = response.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    return list(reader)


def write_event(content_dir, record):
    directory = content_dir / f"seminaire-{record['slug']}"
    ensure_directory(directory)

    fr_path = directory / "index.md"
    en_path = directory / "index.en.md"

    fr_path.write_text(event_frontmatter(record, language='fr'), encoding='utf-8')
    en_record = {
        **record,
        "speaker": record['speaker'],
        "title": record['title'],
        "abstract": record['abstract'],
    }
    en_path.write_text(event_frontmatter(record, language='en'), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Import seminars from the AstroQuébec Google Sheet.")
    parser.add_argument("--url", default=DEFAULT_SHEET_URL)
    parser.add_argument("--content-dir", default="content/event")
    args = parser.parse_args()

    content_dir = Path(args.content_dir)
    if not content_dir.exists():
        content_dir.mkdir(parents=True, exist_ok=True)

    imported = 0
    for row in fetch_rows(args.url):
        record = parse_row(row)
        if not record:
            continue
        write_event(content_dir, record)
        imported += 1

    print(f"Imported {imported} seminar pages")


if __name__ == "__main__":
    main()

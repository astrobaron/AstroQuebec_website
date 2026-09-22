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
DEFAULT_GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs/export?format=csv&gid=0"
DEFAULT_SHAREPOINT_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQuijtqP317H2sYk84mriq9OTQhW624Jwn0RH5nv1OHdKsKTYggxKFnax9GAjG2dkT8OxH7825VrSW/pub?output=csv"
DEFAULT_SOURCE_URLS = [DEFAULT_GOOGLE_SHEET_URL, DEFAULT_SHAREPOINT_URL]
DEFAULT_LOCATION = "Bell Room (Room 103) in the Rutherford building (3600 University) of McGill University"


def normalize_space(value):
    return re.sub(r"\s+", " ", (value or "")).strip()


def slugify(value):
    value = unicodedata.normalize("NFKD", (value or "")).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "seminaire"


def parse_date(value, default_year=None):
    value = normalize_space(value)
    if not value:
        return None

    month_map = {
        "janvier": "January",
        "février": "February",
        "fevrier": "February",
        "mars": "March",
        "avril": "April",
        "mai": "May",
        "juin": "June",
        "juillet": "July",
        "août": "August",
        "aout": "August",
        "septembre": "September",
        "octobre": "October",
        "novembre": "November",
        "décembre": "December",
        "decembre": "December",
    }

    for fmt in ("%d-%b-%Y", "%d-%b-%y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    normalized = value.lower()
    for fr, en in month_map.items():
        if fr in normalized:
            value_en = value
            for fr_month, en_month in month_map.items():
                value_en = re.sub(re.escape(fr_month), en_month, value_en, flags=re.IGNORECASE)
            if default_year:
                try:
                    return datetime.strptime(f"{value_en} {default_year}", "%d %B %Y")
                except ValueError:
                    pass
            for fmt in ("%d %B %Y", "%d %B %y", "%d %B"):
                try:
                    return datetime.strptime(value_en, fmt)
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
    default_year = None
    for key in ("default_year", "year", "AcademicYear", "A2026", "A2025", "A2024"):
        value = row.get(key)
        if value:
            match = re.search(r"(\d{4})", str(value))
            if match:
                default_year = int(match.group(1))
                break

    speaker = normalize_space(row.get("Speaker") or row.get("speaker") or row.get("Nom") or row.get("nom") or "")
    raw_date = normalize_space(row.get("Date") or row.get("date") or row.get("Date ") or "")
    title = normalize_space(row.get("Title") or row.get("title") or row.get("Titre") or row.get("titre") or "")
    abstract = normalize_space(row.get("Abstract") or row.get("abstract") or row.get("Résumé") or row.get("résumé") or row.get("Résumé ") or "")
    affiliation = normalize_space(row.get("Affiliation") or row.get("affiliation") or row.get("Institution") or row.get("institution") or "")
    host = normalize_space(row.get("Host") or row.get("host") or row.get("Hote") or row.get("hote") or "")
    zoom = normalize_space(row.get("Zoom Link") or row.get("zoom_link") or row.get("Zoom") or row.get("Zoom ") or "")

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

    parsed_date = parse_date(raw_date, default_year=default_year)
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


def build_download_url(raw_url):
    url = normalize_space(raw_url)
    if not url:
        return url

    if "docs.google.com/spreadsheets/d/" in url and "/edit" in url:
        matches = re.findall(r"https://docs\.google\.com/spreadsheets/d/[^/]+", url)
        if matches:
            return f"{matches[0]}/export?format=csv&gid=0"

    if "sharepoint.com/" in url:
        if "download=1" in url:
            return url
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}download=1"

    return url


def read_xlsx_rows(content):
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("openpyxl is required to read SharePoint XLSX files.") from exc

    workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    worksheet = workbook.active
    rows = list(worksheet.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [normalize_space(str(cell)) if cell is not None else "" for cell in rows[0]]
    data = []
    for values in rows[1:]:
        row = {}
        for idx, header in enumerate(headers):
            value = values[idx] if idx < len(values) else ""
            row[header] = value
        data.append(row)
    return data


def fetch_rows(url):
    download_url = build_download_url(url)
    try:
        with urlopen(download_url, timeout=60) as response:
            payload = response.read()
    except Exception as exc:
        print(f"Warning: could not fetch seminar source {url}: {exc}", file=sys.stderr)
        return []

    if payload.startswith(b"PK"):
        return read_xlsx_rows(payload)

    text = payload.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return []

    if len(rows) >= 2 and "Responsable" in rows[0] and "Date" in rows[1]:
        header = rows[1]
        year_hint = None
        for cell in rows[0]:
            match = re.search(r"(\d{4})", str(cell or ""))
            if match:
                year_hint = match.group(1)
                break
        parsed_rows = []
        for row in rows[2:]:
            if not row or all((cell or "").strip() == "" for cell in row):
                continue
            if len(row) < len(header):
                row = row + [""] * (len(header) - len(row))
            mapped = {header[i]: row[i] for i in range(len(header))}
            if year_hint:
                mapped["default_year"] = year_hint
            parsed_rows.append(mapped)
        return parsed_rows

    reader = csv.DictReader(io.StringIO(text))
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
    parser = argparse.ArgumentParser(description="Import seminars from the AstroQuébec seminar sources.")
    parser.add_argument("--url", dest="urls", action="append", default=[], help="Seminar source URL. Can be supplied multiple times.")
    parser.add_argument("--content-dir", default="content/event")
    args = parser.parse_args()

    content_dir = Path(args.content_dir)
    if not content_dir.exists():
        content_dir.mkdir(parents=True, exist_ok=True)

    sources = args.urls or DEFAULT_SOURCE_URLS
    imported = 0
    seen = set()

    for url in sources:
        for row in fetch_rows(url):
            record = parse_row(row)
            if not record:
                continue

            key = (record["speaker"], record["date"].date().isoformat(), record["title"])
            if key in seen:
                continue
            seen.add(key)

            write_event(content_dir, record)
            imported += 1

    print(f"Imported {imported} seminar pages")


if __name__ == "__main__":
    main()

import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
MARKER = "# Generated from members_data/cochercheurs.xlsx"


def yaml_string(value):
    return json.dumps(value or "", ensure_ascii=False)


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")


def column_index(cell_reference):
    letters = "".join(char for char in cell_reference if char.isalpha())
    result = 0
    for char in letters:
        result = result * 26 + ord(char.upper()) - ord("A") + 1
    return result - 1


def shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.findall(".//a:t", NS))
        for item in root.findall("a:si", NS)
    ]


def cell_text(cell, strings):
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//a:t", NS))
    value = cell.find("a:v", NS)
    if value is None:
        return ""
    text = value.text or ""
    return strings[int(text)] if cell_type == "s" else text


def first_sheet_path(archive):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
    sheet = workbook.find(".//a:sheets/a:sheet", NS)
    relationship_id = sheet.attrib[f"{{{OFFICE_REL}}}id"]
    target = targets[relationship_id]
    return target if target.startswith("xl/") else f"xl/{target}"


def read_records(workbook_path):
    with zipfile.ZipFile(workbook_path) as archive:
        strings = shared_strings(archive)
        root = ET.fromstring(archive.read(first_sheet_path(archive)))
        rows = []
        for row in root.findall(".//a:sheetData/a:row", NS):
            values = []
            for cell in row.findall("a:c", NS):
                index = column_index(cell.attrib["r"])
                while len(values) <= index:
                    values.append("")
                values[index] = cell_text(cell, strings).strip()
            rows.append(values)

    records = []
    for values in rows[1:]:
        values += [""] * (5 - len(values))
        last_name, first_name, level, email, institution = values[:5]
        if first_name and last_name and level.casefold() == "cochercheur":
            records.append(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "institution": institution or "AstroQuébec",
                }
            )
    return records


def profile(record, slug, language):
    english = language == "en"
    title = f"{record['first_name']} {record['last_name']}"
    role = "Co-Investigator" if english else "Cochercheur ou cochercheuse"
    group = "Co-Investigator" if english else "Cochercheurs et cochercheuses"
    social = (
        "social:\n"
        "  - icon: envelope\n"
        "    icon_pack: fas\n"
        f"    link: {yaml_string('mailto:' + record['email'])}"
        if record["email"]
        else "social: []"
    )
    return f"""---
{MARKER}
title: {yaml_string(title)}
first_name: {yaml_string(record["first_name"])}
last_name: {yaml_string(record["last_name"])}
authors:
  - {yaml_string(slug)}
superuser: false
role: {yaml_string(role)}
organizations:
  - name: {yaml_string(record["institution"])}
    url: ""
bio: ""
interests: []
{social}
email: {yaml_string(record["email"])}
user_groups:
  - {yaml_string(group)}
---
"""


def main():
    workbook_path = Path(sys.argv[1] if len(sys.argv) > 1 else "members_data/cochercheurs.xlsx")
    authors_path = Path(sys.argv[2] if len(sys.argv) > 2 else "content/authors")
    records = read_records(workbook_path)
    for record in records:
        slug = slugify(f"{record['first_name']}-{record['last_name']}")
        profile_path = authors_path / slug
        profile_path.mkdir(parents=True, exist_ok=True)
        (profile_path / "_index.md").write_text(profile(record, slug, "fr"), encoding="utf-8")
        (profile_path / "_index.en.md").write_text(profile(record, slug, "en"), encoding="utf-8")
    print(f"written: {len(records)} bilingual co-investigator profiles")


if __name__ == "__main__":
    main()

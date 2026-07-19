import csv
import re
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

OUTPUT_HEADERS = [
    "Last Name",
    "First Name",
    "Cycle d'études / Graduate studies program",
    "Courriel / Email",
    "Date de début du diplôme / Start date of the degree programme",
    "Établissement d'affiliation / Affiliated institution",
    "Directeur - nom / Director - Last name",
    "Directeur - prénom / Director - first name",
    "Codirecteur1 -  nom / Co-director1 -  Last name",
    "Codirecteur1 - prénom / Co-director1 - first name",
]

ALIASES = {
    "Last Name": ["nom / last name", "nom"],
    "First Name": ["prénom / first name", "prenom / first name", "prénom", "prenom"],
    "Cycle d'études / Graduate studies program": [
        "cycle d'études / graduate studies program",
        "cycle d'etudes / graduate studies program",
        "cycle d'études",
        "cycle d'etudes",
    ],
    "Courriel / Email": ["courriel / email", "courriel", "email"],
    "Date de début du diplôme / Start date of the degree programme": [
        "date de début du diplôme / start date of the degree programme",
        "date de debut du diplome / start date of the degree programme",
        "date de début du diplôme",
        "date de debut du diplome",
    ],
    "Établissement d'affiliation / Affiliated institution": [
        "établissement d'affiliation / affiliated institution",
        "etablissement d'affiliation / affiliated institution",
        "établissement d'affiliation",
        "etablissement d'affiliation",
    ],
    "Directeur - nom / Director - Last name": ["directeur - nom / director - last name", "directeur - nom"],
    "Directeur - prénom / Director - first name": [
        "directeur - prénom / director - first name",
        "directeur - prenom / director - first name",
        "directeur - prénom",
        "directeur - prenom",
    ],
    "Codirecteur1 -  nom / Co-director1 -  Last name": [
        "codirecteur1 - nom / co-director1 - last name",
        "codirecteur1 -  nom / co-director1 -  last name",
        "codirecteur1 - nom",
        "codirecteur1 -  nom",
    ],
    "Codirecteur1 - prénom / Co-director1 - first name": [
        "codirecteur1 - prénom / co-director1 - first name",
        "codirecteur1 - prenom / co-director1 - first name",
        "codirecteur1 - prénom",
        "codirecteur1 - prenom",
    ],
}


def normalize(value):
    value = (value or "").strip().lower()
    value = value.replace("\n", " ")
    value = value.replace("é", "e").replace("è", "e").replace("ê", "e")
    value = value.replace("à", "a").replace("ç", "c")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s*-\s*", " - ", value)
    value = re.sub(r"\s*/\s*", " / ", value)
    return value


def col_index(cell_ref):
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for ch in letters:
        index = index * 26 + ord(ch.upper()) - ord("A") + 1
    return index - 1


def load_shared_strings(zf):
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//a:t", NS)) for si in root.findall("a:si", NS)]


def cell_value(cell, shared_strings):
    cell_type = cell.attrib.get("t")
    value = cell.find("a:v", NS)
    if cell_type == "inlineStr":
        return "".join(t.text or "" for t in cell.findall(".//a:t", NS))
    if value is None:
        return ""
    text = value.text or ""
    if cell_type == "s":
        return shared_strings[int(text)]
    return text


def rows_from_sheet(zf, sheet_path, shared_strings):
    root = ET.fromstring(zf.read(sheet_path))
    rows = []
    for row in root.findall(".//a:sheetData/a:row", NS):
        values = []
        for cell in row.findall("a:c", NS):
            idx = col_index(cell.attrib["r"])
            while len(values) <= idx:
                values.append("")
            values[idx] = cell_value(cell, shared_strings)
        rows.append(values)
    return rows


def sheet_paths(zf):
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets = []
    for sheet in workbook.findall(".//a:sheets/a:sheet", NS):
        rid = sheet.attrib[f"{{{NS['r']}}}id"]
        target = rel_targets[rid]
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheets.append((sheet.attrib["name"], target))
    return sheets


def excel_date(value):
    if not re.fullmatch(r"\d+(\.\d+)?", value or ""):
        return value.strip() if isinstance(value, str) else value
    serial = float(value)
    if serial < 20000:
        return value
    date = datetime(1899, 12, 30) + timedelta(days=serial)
    return date.strftime("%Y-%m-%d")


def clean(value, is_date=False):
    value = str(value or "").strip()
    value = re.sub(r"\s+", " ", value)
    if is_date and value:
        return excel_date(value)
    return value


def column_map(headers):
    normalized = {normalize(header): idx for idx, header in enumerate(headers)}
    mapping = {}
    for output_header, aliases in ALIASES.items():
        for alias in aliases:
            idx = normalized.get(normalize(alias))
            if idx is not None:
                mapping[output_header] = idx
                break
    return mapping


def extract_rows(input_path):
    output_rows = []
    seen = set()
    with zipfile.ZipFile(input_path) as zf:
        shared_strings = load_shared_strings(zf)
        for sheet_name, sheet_path in sheet_paths(zf):
            rows = rows_from_sheet(zf, sheet_path, shared_strings)
            if not rows or sheet_name.lower().startswith("feuil"):
                continue
            mapping = column_map(rows[0])
            if not {"Last Name", "First Name"}.issubset(mapping):
                continue
            for row in rows[1:]:
                record = []
                for header in OUTPUT_HEADERS:
                    idx = mapping.get(header)
                    value = row[idx] if idx is not None and idx < len(row) else ""
                    record.append(clean(value, is_date=header.startswith("Date de début")))
                if not any(record):
                    continue
                key = tuple(record)
                if key in seen:
                    continue
                seen.add(key)
                output_rows.append(record)
    output_rows.sort(key=lambda values: (values[0].lower(), values[1].lower(), values[4]))
    return output_rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_HEADERS)
        writer.writerows(rows)


def xml_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def col_name(index):
    name = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def write_xlsx(path, rows):
    all_rows = [OUTPUT_HEADERS] + rows
    sheet_rows = []
    for r_idx, row in enumerate(all_rows, start=1):
        cells = []
        for c_idx, value in enumerate(row):
            ref = f"{col_name(c_idx)}{r_idx}"
            style = ' s="1"' if r_idx == 1 else ""
            cells.append(f'<c r="{ref}" t="inlineStr"{style}><is><t>{xml_escape(value)}</t></is></c>')
        sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')

    width_xml = "".join(
        f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>'
        for idx, width in enumerate([18, 18, 36, 28, 24, 28, 24, 24, 28, 28], start=1)
    )
    worksheet = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="{NS["a"]}" xmlns:r="{NS["r"]}">
  <cols>{width_xml}</cols>
  <sheetData>{"".join(sheet_rows)}</sheetData>
  <autoFilter ref="A1:J{len(all_rows)}"/>
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
</worksheet>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Students export" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''
    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''
    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", worksheet)
        zf.writestr("xl/styles.xml", styles)
        zf.writestr("docProps/core.xml", core)
        zf.writestr("docProps/app.xml", app)


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("student_data/students_hugo.xlsx")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = extract_rows(input_path)
    csv_path = output_dir / "students_export_list.csv"
    xlsx_path = output_dir / "students_export_list.xlsx"
    write_csv(csv_path, rows)
    write_xlsx(xlsx_path, rows)
    print(f"rows={len(rows)}")
    print(csv_path)
    print(xlsx_path)


if __name__ == "__main__":
    main()

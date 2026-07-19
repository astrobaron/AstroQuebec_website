import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


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
    strings = []
    for si in root.findall("a:si", NS):
        strings.append("".join(t.text or "" for t in si.findall(".//a:t", NS)))
    return strings


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


def rows_from_sheet(zf, sheet_path, shared_strings, limit=10):
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
        if len(rows) >= limit:
            break
    return rows


def sheet_paths(zf):
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels
    }
    sheets = []
    for sheet in workbook.findall(".//a:sheets/a:sheet", NS):
        rid = sheet.attrib[f"{{{NS['r']}}}id"]
        target = rel_targets[rid]
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheets.append((sheet.attrib["name"], target))
    return sheets


def main():
    path = Path(sys.argv[1])
    with zipfile.ZipFile(path) as zf:
        shared_strings = load_shared_strings(zf)
        result = {}
        for name, sheet_path in sheet_paths(zf):
            result[name] = rows_from_sheet(zf, sheet_path, shared_strings)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

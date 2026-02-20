import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
import json
from datetime import datetime
import uuid
import html as html_lib
import re
import time
import os

# ================= CONFIG =================

CASE_LIST_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/submitFirNo"
CASE_DETAIL_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/viewHistory"
HOME_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://services.ecourts.gov.in",
    "referer": "https://services.ecourts.gov.in/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "x-requested-with": "XMLHttpRequest",
}

FIR_SEARCH_PAYLOAD = {
    "police_st_code": "120112",
    "uniform_code": "11191044",
    "state_code": "17",
    "dist_code": "13",
    "court_complex_code": "1170033",
    "est_code": "null",
    "case_status": "Both",
    "ajax_req": "true",
    "app_token": "229b64836be117cecc493c49b76cd3db2abc4d3e45736010bb6e2a41db15e976",
}

CASE_DETAIL_PAYLOAD = {
    "court_code": "",
    "state_code": "",
    "dist_code": "",
    "court_complex_code": "",
    "case_no": "",
    "cino": "",
    "search_flag": "",
    "search_by": "",
    "ajax_req": "true",
    "app_token": "",
}

# ================= GLOBAL SESSION =================

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ================= SECURITY WARMUP =================

def warm_up():
    r = SESSION.get(HOME_URL, timeout=30)
    r.raise_for_status()

# ================= FETCH CASE LIST =================

def fetch_case_list():
    res = SESSION.post(CASE_LIST_URL, data=FIR_SEARCH_PAYLOAD, timeout=30)
    res.raise_for_status()

    soup = BeautifulSoup(res.json().get("case_data", ""), "html.parser")
    cases = []

    for a in soup.select("a[onclick^='viewHistory']"):
        m = re.search(
            r"viewHistory\((\d+),'([^']+)',(\d+),'','([^']+)',(\d+),(\d+),(\d+),'([^']+)'\)",
            a.get("onclick", "")
        )
        if m:
            cases.append({
                "case_no": m.group(1),
                "cino": m.group(2),
                "court_code": m.group(3),
                "search_flag": m.group(4),
                "state_code": m.group(5),
                "dist_code": m.group(6),
                "court_complex_code": m.group(7),
                "search_by": m.group(8),
            })

    return cases

# ================= FETCH CASE DETAIL =================

def fetch_case_html(payload):
    res = SESSION.post(CASE_DETAIL_URL, data=payload, timeout=30)
    res.raise_for_status()
    return res.json()["data_list"]

# ================= PARSING HELPERS =================

def extract_value(soup, label):
    lbl = soup.find("label", string=lambda x: x and label in x)
    if lbl:
        td = lbl.find_parent("td")
        if td:
            nxt = td.find_next_sibling("td")
            if nxt:
                return nxt.get_text(strip=True)
    return None

def extract_case_type(soup):
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2 and tds[0].get_text(strip=True).lower() == "case type":
            return tds[1].get_text(strip=True)
    return None

def extract_fir_details(soup):
    data = {}
    table = soup.find("table", class_="FIR_details_table")
    if table:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 2:
                data[tds[0].get_text(strip=True)] = tds[1].get_text(strip=True)
    return data

# ================= PARSE CASE =================

def parse_case(html_text, payload):
    soup = BeautifulSoup(html_lib.unescape(html_text), "html.parser")

    row = {
        "_id": uuid.uuid4().hex,
        "Update Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Court Name": soup.select_one("#chHeading").get_text(strip=True) if soup.select_one("#chHeading") else None,
        "Case Type": extract_case_type(soup),
        "Filing Date": extract_value(soup, "Filing Date"),
        "Registration Date": extract_value(soup, "Registration Date"),
        "First Hearing Date": extract_value(soup, "First Hearing Date"),
        "Decision Date": extract_value(soup, "Decision Date"),
        "Case Status": extract_value(soup, "Case Status"),
        "Nature of Disposal": extract_value(soup, "Nature of Disposal"),
    }

    reg = extract_value(soup, "Registration Number")
    if reg and "/" in reg:
        row["Case Number"], row["Case Year"] = reg.split("/")
    else:
        row["Case Number"] = row["Case Year"] = None

    fir = extract_fir_details(soup)
    row["Police Station"] = fir.get("Police Station")
    row["FIR Number"] = fir.get("FIR Number")
    row["FIR Year"] = fir.get("Year")

    acts = []
    for tr in soup.select("#act_table tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) >= 2:
            acts.append({"Act": tds[0].get_text(strip=True), "Section": tds[1].get_text(strip=True)})

    row["Acts"] = json.dumps(acts, ensure_ascii=False)
    row.update(payload)
    row["status"] = "success"
    return row

# ================= MAIN =================

def run_all_cases():
    warm_up()
    cases = fetch_case_list()

    wb = Workbook()
    ws = wb.active
    headers_written = False

    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] Fetching case_no={case['case_no']}")

        payload = CASE_DETAIL_PAYLOAD.copy()
        payload.update(case)
        payload["app_token"] = FIR_SEARCH_PAYLOAD["app_token"]

        try:
            html_data = fetch_case_html(payload)
            row = parse_case(html_data, payload)

            if not headers_written:
                ws.append(list(row.keys()))
                headers_written = True

            ws.append(list(row.values()))
            wb.save("ecourts_live.xlsx")

        except Exception as e:
            print("❌ Error:", e)

        time.sleep(0.4)

# ================= ENTRY =================

if __name__ == "__main__":
    run_all_cases()

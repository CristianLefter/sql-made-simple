#!/usr/bin/env python3
"""End-to-end check of the lab page (docs/index.html) in headless Chromium.

Usage: python3 tests/test_lab_browser.py [port]
Serves docs/ over http, runs every golden case through the page's own SQLite engine,
and exercises the answer checker. Requires: pip install playwright && playwright install chromium
"""
import functools, http.server, json, pathlib, sys, threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
failures = []

def fail(m): failures.append(m); print("FAIL:", m)

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "docs"))
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

def run_query(page, sql):
    page.fill("#sql", sql)
    page.click("#run")
    page.wait_for_timeout(50)

def read_result(page):
    err = page.query_selector("#results .msg.err")
    if err: return {"error": err.inner_text()}
    tbl = page.query_selector("#results table")
    if not tbl: return {"rows": None, "text": page.inner_text("#results")}
    cols = [c.inner_text() for c in page.query_selector_all("#results thead th")]
    rows = [[c.inner_text() for c in r.query_selector_all("td")] for r in page.query_selector_all("#results tbody tr")]
    return {"cols": cols, "rows": rows}

def as_text(v):
    return "NULL" if v is None else (str(int(v)) if isinstance(v, (int, float)) and float(v) == int(v) else str(v))

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1100, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{PORT}/index.html")
    page.wait_for_selector("html[data-ready=true]", timeout=20000)
    print("engine:", page.inner_text("#engine"))

    # 1. Starting query returns 5
    page.click("#run"); page.wait_for_timeout(50)
    r = read_result(page)
    if r.get("rows") != [["5"]]: fail(f"starting query: {r}")

    # 2. Golden cases through the page
    for path in sorted((ROOT / "tests" / "golden").glob("*.json")):
        data = json.loads(path.read_text())
        for c in data["cases"]:
            run_query(page, c["sql"]); r = read_result(page)
            if "error" in r: fail(f"{c['id']}: {r['error']}"); continue
            got_rows = r.get("rows") or []
            want = [[as_text(v) for v in row] for row in c["rows"]]
            if c["rows"] == []:
                if r.get("rows") is not None and got_rows: fail(f"{c['id']}: expected empty")
                continue
            if r["cols"] != c["columns"]: fail(f"{c['id']}: columns {r['cols']}")
            if sorted(map(tuple, got_rows)) != sorted(map(tuple, want)): fail(f"{c['id']}: rows {got_rows} != {want}")
        for c in data.get("errors", []):
            run_query(page, c["sql"]); r = read_result(page)
            if r.get("error") != "The database says: " + c["message"]: fail(f"{c['id']}: {r}")

    # 3. Foreign keys are enforced in the page's engine
    run_query(page, "INSERT INTO Orders VALUES (999, 42, '2026-03-01');")
    r = read_result(page)
    if "FOREIGN KEY constraint failed" not in r.get("error", ""): fail(f"foreign keys not enforced: {r}")

    # 4. Reset restores the database after a change
    run_query(page, "DELETE FROM Customers WHERE CustomerID = 5;")
    run_query(page, "SELECT COUNT(*) FROM Customers;")
    if read_result(page).get("rows") != [["4"]]: fail("delete did not take effect")
    page.click("#reset"); run_query(page, "SELECT COUNT(*) FROM Customers;")
    if read_result(page).get("rows") != [["5"]]: fail("reset did not restore")

    # 5. Answer checker: correct, wrong columns, wrong row count, wrong values, reordered rows
    def check(challenge, sql):
        page.select_option("#challenge-select", challenge)
        page.fill("#sql", sql); page.click("#check"); page.wait_for_timeout(50)
        return page.inner_text("#results .msg")
    t = check("ch1-prove", "SELECT ProductName, UnitPrice FROM Products;")
    if not t.startswith("Correct"): fail(f"checker should accept: {t}")
    t = check("ch1-prove", "SELECT ProductName, UnitPrice FROM Products ORDER BY UnitPrice DESC;")
    if not t.startswith("Correct"): fail(f"multiset should ignore order: {t}")
    t = check("ch1-prove", "SELECT UnitPrice, ProductName FROM Products;")
    if "columns should be" not in t: fail(f"column order not detected: {t}")
    t = check("ch1-prove", "SELECT ProductName, UnitPrice FROM Products WHERE UnitPrice > 10;")
    if "Expected 6 rows" not in t: fail(f"row count not detected: {t}")
    t = check("ch1-prove", "SELECT CustomerName, City FROM Customers;")
    if "columns should be" not in t: fail(f"wrong table not detected: {t}")
    t = check("ch1-prove", "SELECT ProductName, UnitPrice + 1 AS UnitPrice FROM Products;")
    if "values differ" not in t: fail(f"value difference not detected: {t}")
    t = check("ch1-names", "SELECT City FROM Customers;")
    if "columns should be" not in t: fail(f"names challenge: {t}")
    # duplicates must count: 5 rows with a repeated name is not the same multiset
    t = check("ch1-names", "SELECT 'Maya Chen' AS CustomerName FROM Customers;")
    if "values differ" not in t: fail(f"duplicate counts not enforced: {t}")

    # 6. Regression: checking answers must never change the active database.
    # The exact failing behavior observed in the published lab was an UPDATE
    # entered in the editor followed by Check my answer (without Run).
    t = check("ch1-prove", "UPDATE Products SET ProductName = 'Checker Test' WHERE ProductID = 6;")
    if "read-only queries" not in t: fail(f"checker should reject UPDATE: {t}")
    run_query(page, "SELECT ProductName FROM Products WHERE ProductID = 6;")
    if read_result(page).get("rows") != [["Backpack"]]: fail("checker modified active data")

    # A write followed by a matching SELECT must not bypass the checker.
    t = check("ch1-prove", "UPDATE Products SET ProductName = 'Checker Test' WHERE ProductID = 6; SELECT ProductName, UnitPrice FROM Products;")
    if "read-only queries" not in t: fail(f"multi-statement write accepted: {t}")
    run_query(page, "SELECT ProductName FROM Products WHERE ProductID = 6;")
    if read_result(page).get("rows") != [["Backpack"]]: fail("multi-statement checker modified active data")

    # A separate read-only assessment should use the canonical dataset even
    # when the learner has modified their own working copy via Run.
    run_query(page, "UPDATE Products SET ProductName = 'Scratchpad' WHERE ProductID = 6;")
    t = check("ch1-prove", "SELECT ProductName, UnitPrice FROM Products;")
    if not t.startswith("Correct"): fail(f"checker leaked learner edits: {t}")
    run_query(page, "SELECT ProductName FROM Products WHERE ProductID = 6;")
    if read_result(page).get("rows") != [["Scratchpad"]]: fail("checker overwrote learner workspace")
    page.click("#reset")

    # 7. Deep link prefill
    page.goto(f"http://127.0.0.1:{PORT}/index.html?q=SELECT%20City%20FROM%20Customers%3B&challenge=ch1-prove")
    page.wait_for_selector("html[data-ready=true]")
    if page.input_value("#sql") != "SELECT City FROM Customers;" or page.input_value("#challenge-select") != "ch1-prove":
        fail("deep link did not prefill")

    # 8. Screenshots: desktop light, desktop dark, phone
    page.goto(f"http://127.0.0.1:{PORT}/index.html"); page.wait_for_selector("html[data-ready=true]")
    run_query(page, "SELECT CustomerName, City\nFROM Customers;")
    out = ROOT / "tests" / "screenshots"; out.mkdir(exist_ok=True)
    page.screenshot(path=str(out / "desktop-light.png"))
    page.emulate_media(color_scheme="dark"); page.screenshot(path=str(out / "desktop-dark.png"))
    page.emulate_media(color_scheme="light")
    page.set_viewport_size({"width": 390, "height": 800}); page.screenshot(path=str(out / "phone.png"), full_page=True)
    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    if overflow: fail("page scrolls horizontally on a 390px phone")

    if errors: fail(f"page errors: {errors}")
    b.close()

print(f"browser checks done, {len(failures)} failure(s)")
sys.exit(1 if failures else 0)

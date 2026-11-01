#!/usr/bin/env python3
"""Golden-result checks for SQL Made Simple (SQLite).

Each case declares how results are compared:
  multiset - same columns, same rows with duplicate counts preserved, order ignored
  ordered  - same columns, same rows in the same order (the query must contain ORDER BY)
Numbers compare by value (28 equals 28.0). NULL stays None.
"""
import json, pathlib, sqlite3, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETUP = ROOT / "database" / "sqlite" / "setup.sql"
failures = []

def fail(msg):
    failures.append(msg)
    print("FAIL:", msg)

def norm(v):
    return v if v is None or isinstance(v, str) else float(v)

def fresh_db():
    con = sqlite3.connect(":memory:")
    con.executescript(SETUP.read_text())
    return con

def check_environment(con):
    if con.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        fail("foreign keys are not enabled after running setup.sql")
    if con.execute("PRAGMA foreign_key_check").fetchall():
        fail("foreign_key_check reports violations in the seed data")
    for table, n in {"Customers": 5, "Products": 6, "Orders": 8, "OrderItems": 13}.items():
        got = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if got != n:
            fail(f"{table} has {got} rows, expected {n}")
    web_copy = ROOT / "docs" / "setup.sql"
    if web_copy.read_text() != SETUP.read_text():
        fail("docs/setup.sql differs from database/sqlite/setup.sql (copy it over)")

def check_case(con, case):
    cur = con.execute(case["sql"])
    cols = [d[0] for d in cur.description]
    rows = [[norm(v) for v in r] for r in cur.fetchall()]
    want = [[norm(v) for v in r] for r in case["rows"]]
    if [c.lower() for c in cols] != [c.lower() for c in case["columns"]]:
        return fail(f"{case['id']}: columns {cols} != {case['columns']}")
    mode = case["mode"]
    if mode == "ordered":
        if "order by" not in case["sql"].lower():
            return fail(f"{case['id']}: ordered mode needs ORDER BY in the query")
        ok = rows == want
    else:
        ok = Counter(map(tuple, rows)) == Counter(map(tuple, want))
    if not ok:
        fail(f"{case['id']}: rows differ\n   got:  {rows}\n   want: {want}")

def check_error(con, case):
    try:
        con.execute(case["sql"]).fetchall()
    except sqlite3.Error as e:
        if str(e) != case["message"]:
            fail(f"{case['id']}: message {str(e)!r} != {case['message']!r}")
        return
    fail(f"{case['id']}: expected an error but the query succeeded")

def main():
    con = fresh_db()
    check_environment(con)
    total = 0
    for path in sorted((ROOT / "tests" / "golden").glob("*.json")):
        data = json.loads(path.read_text())
        for case in data["cases"]:
            check_case(con, case); total += 1
        for case in data.get("errors", []):
            check_error(con, case); total += 1
    print(f"{total} golden cases checked, {len(failures)} failure(s)")
    sys.exit(1 if failures else 0)

main()

# SQL Made Simple: lab and companion files

Companion repository for the book *SQL Made Simple*. It has three parts:

| Part | Where | Purpose |
|---|---|---|
| **Browser lab** | `docs/` | The first stop for every reader. SQLite runs in the browser, SimpleStore is preloaded, nothing to install, no account. |
| **Codespaces** | `.devcontainer/` | The extended environment: a terminal with `sqlite3`, the database prebuilt, and a SQL extension. |
| **Scripts and checks** | `database/`, `tests/` | The SimpleStore setup script and the golden-result checks that keep the book and the lab in agreement. |

## For readers

Open the lab: **(your GitHub Pages address goes here)**

1. The first query is already in the box. Press **Run** (or Ctrl+Enter). You should see **5**.
2. Use **Check my answer** to test your own solutions to the book's tasks.
3. Changes are never saved. **Reset database** or a page reload restores SimpleStore.

No account? The lab is all you need for the first chapters. You can also run `database/sqlite/setup.sql` in any SQLite tool.

## For the author

### Publish the lab (GitHub Pages)
Repository Settings, Pages, "Deploy from a branch", branch `main`, folder `/docs`. The lab is a static site: `docs/index.html`, `docs/setup.sql`, `docs/challenges.json`, and `docs/vendor/` (SQLite compiled to WebAssembly, [sql.js](https://github.com/sql-js/sql.js), MIT licence, vendored so the lab does not depend on any other site).

Opening `docs/index.html` straight from disk will not work, because browsers block loading the database engine from a file address. Serve it instead: `python3 -m http.server --directory docs 8000`.

### Keep the book and the lab in agreement
`database/sqlite/setup.sql` is the single source of truth. After changing it, copy it to `docs/setup.sql` (the test fails if they differ).

Golden results live in `tests/golden/chapter-NN.json`. Each case declares how it is compared:

- `multiset`: same columns, same rows with duplicate counts preserved, order ignored.
- `ordered`: same rows in the same order. The query must contain `ORDER BY`.

Numbers compare by value (28 equals 28.0). Error-message cases pin the exact SQLite wording printed in the book.

```
python3 tests/run_golden.py            # fast, no dependencies
python3 tests/test_lab_browser.py      # runs the same cases through the lab page (needs Playwright + Chromium)
```

### Adding a task to "Check my answer"
Add an entry to `docs/challenges.json` with `id`, `title`, `prompt`, `solution` (a query whose result is the expected answer) and `mode` (`multiset` or `ordered`). Solutions are visible to anyone who views the page source. That is acceptable for self-checking, not for assessment.

### Status
- Verified: setup script, golden cases, the lab page (including answer checking, reset, foreign keys, phone layout) in headless Chromium.
- **Not yet verified:** the Codespaces configuration (build time, the SQLite extension's behaviour, first-run experience) and the GitHub Pages deployment. Test both from a real GitHub account before the book refers to them.

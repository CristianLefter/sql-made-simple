# SQL Made Simple — Quick Start

This guide gets you from opening the lab to running your first SQL query. The **browser lab is the recommended way** to follow Chapter 1. You do not need a GitHub account or programming experience.

## Option 1: Browser lab (recommended)

1. Open https://cristianlefter.github.io/sql-made-simple/ in a modern browser.
2. Wait until the lab reports that SQLite is ready. The SQL editor starts with this query:

   ```sql
   SELECT COUNT(*) FROM Customers;
   ```

3. Select **Run**, or press **Ctrl+Enter** (on a Mac, **Cmd+Enter**). The result should contain one value: **5**.
4. Replace the editor text with the next query in the book. Select **Run** again.
5. For **Prove you can do it**, choose **Chapter 1, Prove you can do it: products and prices** from the **Check my answer** selector, then select **Check my answer**. This checks column order, rows and values; it does not require any particular row order.

### If something goes wrong

| What you see | What to try |
| --- | --- |
| The editor or buttons never become ready | Refresh the page and check that the browser can load the site and its files. Record any startup error message. |
| A result other than **5** for the first query | Select **Reset database**, then run `SELECT COUNT(*) FROM Customers;` again. |
| `no such table: Customers` | Select **Reset database**. Make sure you used `Customers` (plural) and did not delete the table while experimenting. |
| `no such column: Citty` | Correct `Citty` to `City`. |
| The query runs, but there are no rows | Recheck your `WHERE` condition, including quotes and capitalization of text values. |
| **Check my answer** reports wrong columns | For the products exercise, return `ProductName` followed by `UnitPrice`. |
| **Check my answer** reports wrong rows or values | The checker uses the original sample data. Select **Reset database** to restore your own workspace if you changed it. |

The browser lab does **not save changes** between page loads. **Reset database** restores the original SimpleStore data without reloading the page. A refresh also starts again from the provided dataset.

## Option 2: Local SQLite (optional)

If you already have SQLite installed, run the repository's `database/sqlite/setup.sql` script in a fresh SQLite database. For example, from the repository root:

```sh
sqlite3 simplestore.db < database/sqlite/setup.sql
sqlite3 simplestore.db
```

Then enter the SQL examples from the chapter in the `sqlite3` prompt. If you have used the same database file before, choose a new file name before recreating the sample, because the setup script creates the tables.

## Option 3: GitHub Codespaces (planned, not required)

A Codespaces configuration is planned as an optional advanced setup. It is **not present in the current published repository**, so these steps are not offered as a working path yet. Codespaces would require a GitHub account and its availability or included usage would depend on your account. Use the browser lab to complete Chapter 1.

## Your first successful result

You are ready to continue when this query returns **5**:

```sql
SELECT COUNT(*) FROM Customers;
```

Return to [Chapter 1](source/chapter-01.md).

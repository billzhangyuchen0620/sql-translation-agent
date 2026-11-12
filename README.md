# SQL Dialect Translation & Validation Agent

A small agent that mimics the core pipeline of an enterprise data-warehouse
migration: translate legacy SQL Server (T-SQL) queries into Snowflake dialect
with an LLM, then verify the translation by executing both versions and
comparing result sets. Failed translations are fed back to the model with
the observed diff for self-correction (up to 2 rounds).

## How it works

1. **Translate** - an LLM (gpt-4o-mini, temperature 0) converts T-SQL to Snowflake SQL.
2. **Execute** - the translation runs against a sample database (DuckDB, used
   locally as a Snowflake stand-in; see Limitations).
3. **Compare** — result sets are normalized (string-cast, row-sorted) and
   compared cell-by-cell against a hand-written reference query.
4. **Self-correct** — on mismatch, the diff/error is sent back to the model
   for a corrected translation (up to 2 rounds).

## Evaluation

Test set: 16 queries. The first 10 cover common dialect pitfalls
(TOP→LIMIT, GETDATE()→CURRENT_DATE, ISNULL→COALESCE, bracket identifiers,
string concatenation, LEN→LENGTH), including 2 already-compatible control
cases. Six harder cases were added later: date arithmetic (DATEADD),
DATEDIFF argument style, DATEPART argument style, CHARINDEX→INSTR,
EOMONTH→LAST_DAY, and one composite report query that combines four
pitfalls in a single statement.

**First-try pass rate: 88% (14/16)**
**After self-correction: 94% (15/16)**

The self-correction loop recovered one case on its own: the DATEDIFF case
failed its first attempt and passed after one correction round.

Full run output:

```
Case  1 | first-try: True | final: True | attempts: 1
Case  2 | first-try: True | final: True | attempts: 1
Case  3 | first-try: True | final: True | attempts: 1
Case  4 | first-try: True | final: True | attempts: 1
Case  5 | first-try: True | final: True | attempts: 1
Case  6 | first-try: True | final: True | attempts: 1
Case  7 | first-try: True | final: True | attempts: 1
Case  8 | first-try: True | final: True | attempts: 1
Case  9 | first-try: True | final: True | attempts: 1
Case 10 | first-try: True | final: True | attempts: 1
Case 11 | first-try: False | final: False | attempts: 3
Case 12 | first-try: False | final: True | attempts: 2
Case 13 | first-try: True | final: True | attempts: 1
Case 14 | first-try: True | final: True | attempts: 1
Case 15 | first-try: True | final: True | attempts: 1
Case 16 | first-try: True | final: True | attempts: 1

=== SUMMARY ===
First-try pass rate : 88%
Final pass rate     : 94%
```

Full per-case results: `results/evaluation.csv`

## Failure analysis

Case 11 (DATEADD) failed all three attempts. The model consistently
produced `DATEADD(day, 90, hire_date)` — valid Snowflake SQL — but the
local validation stand-in (DuckDB) has no DATEADD function, so every
attempt failed at execution, and the correction loop never switched to
the equivalent `hire_date + INTERVAL 90 DAY` form. The failure is a
coverage gap between the validation stand-in and the target dialect, not
a translation error; a dialect-compatibility note in the prompt or a shim
in the validator would close it.

## Limitations

- DuckDB stands in for Snowflake locally. A few Snowflake-valid constructs
  (e.g. DATEADD) are not executable in DuckDB — see Failure analysis.
- Comparison is result-set based: it proves equivalence on this sample
  data, not for all possible data.

## Run it

1. `pip install -r requirements.txt`
2. Put your `OPENAI_API_KEY` in a `.env` file in this folder.
3. `python3 agent.py`

Results are printed per case and written to `results/evaluation.csv`.

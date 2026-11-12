import os
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from schema_and_data import build_db
from test_cases import TEST_CASES

#Function of translating
load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = (
    "You are an expert SQL translator. Translate the given SQL Server (T-SQL) query "
    "into Snowflake SQL. Rules: output ONLY the translated SQL. No markdown code fences, "
    "no explanations, no comments. Preserve the query's logic exactly."
)


def translate(tsql):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": tsql},
        ],
    )
    sql = resp.choices[0].message.content.strip()
    sql = re.sub(r"^```(sql)?|```$", "", sql, flags=re.MULTILINE).strip()
    return sql

#Function of comparing
def run_sql(con, sql):
    return con.execute(sql).fetchdf()

def normalize(df):
    df = df.astype(str)
    if len(df.columns) > 0:
        df = df.sort_values(by=list(df.columns))
    return df.reset_index(drop=True)

def results_match(con, translated_sql, reference_sql):
    expected = normalize(run_sql(con, reference_sql))
    try:
        actual = normalize(run_sql(con, translated_sql))
    except Exception as e:
        return False, f"Execution error: {e}"
    if expected.equals(actual):
        return True, ""
    diff = f"Row counts — expected: {len(expected)}, actual: {len(actual)}. "
    if len(expected.columns) == len(actual.columns):
        diff += f"Expected head: {expected.head(3).to_dict('records')}; Actual head: {actual.head(3).to_dict('records')}"
    return False, diff

#Function of auto-correcting and re-running
def fix_translation(tsql, bad_sql, problem):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":
                f"Original T-SQL:\n{tsql}\n\nYour previous Snowflake translation:\n{bad_sql}\n\n"
                f"Problem found when validating it:\n{problem}\n\n"
                "Output ONLY the corrected Snowflake SQL."},
        ],
    )
    sql = resp.choices[0].message.content.strip()
    sql = re.sub(r"^```(sql)?|```$", "", sql, flags=re.MULTILINE).strip()
    return sql

def main():
    con = build_db()
    rows = []
    for case in TEST_CASES:
        translated = translate(case["tsql"])
        ok, problem = results_match(con, translated, case["reference"])
        first_try = ok
        attempts = 1
        while not ok and attempts <= 2:
            translated = fix_translation(case["tsql"], translated, problem)
            ok, problem = results_match(con, translated, case["reference"])
            attempts += 1
        rows.append({
            "id": case["id"],
            "pitfall": case["pitfall"],
            "first_try_pass": first_try,
            "final_pass": ok,
            "attempts": attempts,
            "final_sql": translated,
        })
        print(f"Case {case['id']:>2} | first-try: {first_try} | final: {ok} | attempts: {attempts}")
    df = pd.DataFrame(rows)
    df.to_csv("results/evaluation.csv", index=False)
    print("\n=== SUMMARY ===")
    print(f"First-try pass rate : {df['first_try_pass'].mean():.0%}")
    print(f"Final pass rate     : {df['final_pass'].mean():.0%}")

if __name__ == "__main__":
    main()

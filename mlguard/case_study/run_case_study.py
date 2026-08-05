from pathlib import Path
from mlguard.core.loaders import load_data
from mlguard.core.runner import run_audit


def audit_case_studies():
    base_dir = Path(__file__).parent
    
    bank_path = base_dir / "bank_churn_pitfalls.csv"
    if bank_path.exists():
        df_bank = load_data(bank_path)
        findings_bank = run_audit(df_bank, target_col="is_churn")
        print(f"BANKING AUDIT RESULTS ({len(findings_bank)} findings):")
        for item in findings_bank:
            print(f"  [{item['severity']}] {item['check']} ({item['column']}): {item['message']}")

    retail_path = base_dir / "retail_sales_pitfalls.csv"
    if retail_path.exists():
        df_retail = load_data(retail_path)
        findings_retail = run_audit(df_retail, time_col="date")
        print(f"\nRETAIL SALES AUDIT RESULTS ({len(findings_retail)} findings):")
        for item in findings_retail:
            print(f"  [{item['severity']}] {item['check']} ({item['column']}): {item['message']}")


if __name__ == "__main__":
    audit_case_studies()

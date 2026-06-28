import pandas as pd
from typing import Tuple, List


def validate_telco_data(df) -> Tuple[bool, List[str]]:
    """
    Comprehensive data validation for Telco Customer Churn dataset.
    """
    print("🔍 Starting data validation with Great Expectations...")

    failed_expectations = []
    total_checks = 0

    def check(name, condition):
        nonlocal total_checks
        total_checks += 1
        if not condition:
            failed_expectations.append(name)

    # === SCHEMA VALIDATION ===
    print("   📋 Validating schema and required columns...")

    required_columns = ["customerID", "gender", "Partner", "Dependents",
                        "PhoneService", "InternetService", "Contract",
                        "tenure", "MonthlyCharges", "TotalCharges"]

    for col in required_columns:
        check(f"expect_column_to_exist:{col}", col in df.columns)

    check("expect_customerID_not_null", df["customerID"].notnull().all() if "customerID" in df.columns else False)

    # === BUSINESS LOGIC VALIDATION ===
    print("   💼 Validating business logic constraints...")

    if "gender" in df.columns:
        check("expect_gender_values", df["gender"].isin(["Male", "Female"]).all())
    if "Partner" in df.columns:
        check("expect_Partner_values", df["Partner"].isin(["Yes", "No"]).all())
    if "Dependents" in df.columns:
        check("expect_Dependents_values", df["Dependents"].isin(["Yes", "No"]).all())
    if "PhoneService" in df.columns:
        check("expect_PhoneService_values", df["PhoneService"].isin(["Yes", "No"]).all())
    if "Contract" in df.columns:
        check("expect_Contract_values", df["Contract"].isin(["Month-to-month", "One year", "Two year"]).all())
    if "InternetService" in df.columns:
        check("expect_InternetService_values", df["InternetService"].isin(["DSL", "Fiber optic", "No"]).all())

    # === NUMERIC RANGE VALIDATION ===
    print("   📊 Validating numeric ranges and business constraints...")

    if "tenure" in df.columns:
        check("expect_tenure_not_null", df["tenure"].notnull().all())
        check("expect_tenure_range", df["tenure"].between(0, 120).all())
    if "MonthlyCharges" in df.columns:
        check("expect_MonthlyCharges_not_null", df["MonthlyCharges"].notnull().all())
        check("expect_MonthlyCharges_range", df["MonthlyCharges"].between(0, 200).all())
    if "TotalCharges" in df.columns:
        total_charges = pd.to_numeric(df["TotalCharges"], errors="coerce")
        check("expect_TotalCharges_non_negative", (total_charges.dropna() >= 0).all())

    # === DATA CONSISTENCY CHECKS ===
    print("   🔗 Validating data consistency...")

    if "TotalCharges" in df.columns and "MonthlyCharges" in df.columns:
        total = pd.to_numeric(df["TotalCharges"], errors="coerce")
        monthly = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
        mostly = (total >= monthly).mean()
        check("expect_TotalCharges_gte_MonthlyCharges", mostly >= 0.95)

    # === RESULTS ===
    passed_checks = total_checks - len(failed_expectations)
    is_valid = len(failed_expectations) == 0

    if is_valid:
        print(f"✅ Data validation PASSED: {passed_checks}/{total_checks} checks successful")
    else:
        print(f"❌ Data validation FAILED: {len(failed_expectations)}/{total_checks} checks failed")
        print(f"   Failed expectations: {failed_expectations}")

    return is_valid, failed_expectations
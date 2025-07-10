# your_app/data_analysis.py
import pandas as pd
from .models import FeasibilityStudy

def analyze_project_data():
    queryset = FeasibilityStudy.objects.all().values(
        'funding_required',
        'roi_period_months',
        'marketing_investment_percentage'
    )

    df = pd.DataFrame(queryset)

    if df.empty:
        return {"error": "No data available."}

    return {
        "average_funding_required": float(df["funding_required"].mean()),
        "max_roi_period_months": int(df["roi_period_months"].max()),
        "min_marketing_percentage": int(df["marketing_investment_percentage"].min())
    }

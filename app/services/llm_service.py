import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


def classify_transactions(transactions):

    prompt = f"""
For each merchant assign one category.

Possible categories:

Food
Shopping
Travel
Transport
Utilities
Cash Withdrawal
Entertainment
Other

Transactions:

{transactions}

Return only JSON list.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return json.loads(response.text)


def generate_narrative_summary(data):

    prompt = f"""
Generate JSON with these fields:

total_spend_inr
total_spend_usd
top_3_merchants
anomaly_count
narrative
risk_level

Data:

{data}

Return ONLY valid JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    try:

        text = response.text.strip()

        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        return json.loads(text)

    except:

        return {
            "total_spend_inr": data["total_spend_inr"],
            "total_spend_usd": data["total_spend_usd"],
            "top_3_merchants": data["top_3_merchants"],
            "anomaly_count": data["anomaly_count"],
            "narrative": "Spending pattern appears normal.",
            "risk_level": "Moderate"
        }
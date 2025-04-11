import os
import requests


# External API settings
EXTERNAL_API_BASE = "https://pagos-prod.studio.lyzr.ai/api/v1/usages"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


def deduct_usage(organization_id: str, count: float, usage_type="actions",):
    # Build the URL with path and query parameters
    url = f"{EXTERNAL_API_BASE}/{organization_id}/deduct/{usage_type}"
    params = {"count": count}

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        return {
            "status": "success",
            "data": response.json()
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")

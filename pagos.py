import os
import requests
from dotenv import load_dotenv

load_dotenv()


# External API settings
EXTERNAL_API_BASE = "https://pagos-prod.studio.lyzr.ai/api/v1"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


def deduct_usage(organization_id: str, count: float, usage_type="actions",):
    # Build the URL with path and query parameters
    url = f"{EXTERNAL_API_BASE}/usages/{organization_id}/deduct/{usage_type}"
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


def get_organization_id(api_key:str):
    url = f"{EXTERNAL_API_BASE}/keys/user"
    params = {"api_key": api_key}

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return {
            "status": "success",
            "data": response['data']['org_id']
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")

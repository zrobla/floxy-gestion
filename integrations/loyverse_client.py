import json
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.utils import timezone

from integrations.models import LoyverseStore


def _get_token() -> Optional[str]:
    store = LoyverseStore.objects.order_by("-created_at").first()
    return store.token if store else None


def _build_url(base_url: str, path: str, params: dict) -> str:
    query = urlencode({k: v for k, v in params.items() if v is not None})
    return f"{base_url}{path}?{query}" if query else f"{base_url}{path}"


def fetch_receipts(since_datetime: Optional[datetime] = None) -> List[dict]:
    token = _get_token()
    if not token:
        raise RuntimeError("Jeton Loyverse manquant.")

    base_url = "https://api.loyverse.com/v1.0"
    path = "/receipts"
    receipts: List[dict] = []
    cursor = None
    limit = 250

    if since_datetime is not None and timezone.is_naive(since_datetime):
        since_datetime = timezone.make_aware(since_datetime)

    while True:
        params = {
            "limit": limit,
            "since": since_datetime.isoformat() if since_datetime else None,
            "cursor": cursor,
        }
        url = _build_url(base_url, path, params)
        request = Request(url)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Content-Type", "application/json")

        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))

        receipts.extend(payload.get("receipts", []))
        cursor = payload.get("cursor") or payload.get("next_cursor")
        if not cursor:
            break

    return receipts

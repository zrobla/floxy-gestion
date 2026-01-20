import hashlib
import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from integrations.loyverse_client import fetch_receipts
from integrations.models import LoyverseReceipt, LoyverseStore


def _get_receipt_identifier(data: dict) -> str:
    receipt_id = data.get("id") or data.get("receipt_id") or data.get("receipt_number")
    if receipt_id:
        return str(receipt_id)
    payload = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class Command(BaseCommand):
    help = "Synchronise les reçus Loyverse sans doublons."

    def add_arguments(self, parser):
        parser.add_argument(
            "--since",
            dest="since",
            help="Date ISO pour limiter la synchronisation (ex: 2024-01-01T00:00:00).",
        )

    def handle(self, *args, **options):
        store = LoyverseStore.objects.order_by("-created_at").first()
        if not store or not store.token:
            self.stdout.write(
                self.style.WARNING(
                    "Aucun jeton Loyverse configuré. Synchronisation ignorée."
                )
            )
            return

        since_value = options.get("since")
        since_datetime = None
        if since_value:
            try:
                since_datetime = timezone.datetime.fromisoformat(since_value)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR("Format de date invalide pour --since.")
                )
                return

        try:
            receipts = fetch_receipts(since_datetime=since_datetime)
        except RuntimeError:
            self.stdout.write(
                self.style.WARNING("Jeton Loyverse manquant. Synchronisation ignorée.")
            )
            return
        created = 0
        skipped = 0

        for receipt in receipts:
            receipt_id = _get_receipt_identifier(receipt)
            if LoyverseReceipt.objects.filter(receipt_id=receipt_id).exists():
                skipped += 1
                continue
            LoyverseReceipt.objects.create(receipt_id=receipt_id, raw_json=receipt)
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Reçus importés : {created} | Reçus ignorés : {skipped}"
            )
        )

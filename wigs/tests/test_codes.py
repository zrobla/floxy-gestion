from django.db import transaction
from django.test import TestCase

from wigs.models import CareWig, Sequence, WigProduct


class WigCodeTests(TestCase):
    def test_wig_product_codes_unique(self):
        products = [
            WigProduct.objects.create(name=f"Perruque {idx}") for idx in range(3)
        ]
        codes = [product.code for product in products]

        self.assertEqual(len(set(codes)), 3)
        for code in codes:
            self.assertTrue(code.startswith("WIG-"))

    def test_care_wig_codes_unique(self):
        care_items = [
            CareWig.objects.create(client=f"Cliente {idx}") for idx in range(3)
        ]
        codes = [item.code for item in care_items]

        self.assertEqual(len(set(codes)), 3)
        for code in codes:
            self.assertTrue(code.startswith("CARE-"))

    def test_sequence_increments_for_same_period(self):
        with transaction.atomic():
            first = WigProduct.objects.create(name="Perruque A")
            second = WigProduct.objects.create(name="Perruque B")

        sequence = Sequence.objects.get(key=first.code.rsplit("-", 1)[0])
        self.assertEqual(sequence.value, 2)
        self.assertNotEqual(first.code, second.code)

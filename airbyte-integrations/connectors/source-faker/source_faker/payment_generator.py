#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import os
import random
from typing import Dict, List

from .purchase_generator import PurchaseGenerator
from .utils import format_airbyte_time, read_json


CURRENCIES = ["USD", "EUR", "GBP"]
METHODS = ["card", "paypal", "bank_transfer", "apple_pay", "google_pay"]


class PaymentGenerator:
    def __init__(self, stream_name: str, seed: int) -> None:
        self.stream_name = stream_name
        self.seed = seed
        self.purchase_generator = PurchaseGenerator("purchases", seed)
        dirname = os.path.dirname(os.path.realpath(__file__))
        products = read_json(os.path.join(dirname, "record_data", "products.json"))
        self.product_prices: Dict[int, int] = {product["id"]: product["price"] for product in products}

    def prepare(self):
        self.purchase_generator.prepare()

    def generate(self, user_id: int) -> List[Dict]:
        """
        Generates one payment per completed purchase (a cart whose purchased_at is set).
        Returns plain dicts, not messages; payment ids are assigned by the stream so they stay sequential.
        """

        payments: List[Dict] = []
        for message in self.purchase_generator.generate(user_id):
            purchase = message.record.data
            if purchase["purchased_at"] is None:
                continue

            # currency and method are drawn from a separate RNG so the mimesis sequence is never touched
            rng = random.Random(f"{self.seed}:{purchase['id']}") if self.seed is not None else random.Random()

            paid_at = purchase["purchased_at"]
            payment = {
                "purchase_id": purchase["id"],
                "user_id": purchase["user_id"],
                "amount": round(float(self.product_prices[purchase["product_id"]]), 2),
                "currency": rng.choice(CURRENCIES),
                "method": rng.choice(METHODS),
                "status": "refunded" if purchase["returned_at"] is not None else "captured",
                "paid_at": paid_at,
                "created_at": paid_at,
                "updated_at": format_airbyte_time(datetime.datetime.now()),
            }
            payments.append(payment)

        return payments

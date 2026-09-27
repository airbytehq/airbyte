#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import List

from mimesis import Numeric, Text
from mimesis.locales import Locale

from airbyte_cdk.models import AirbyteRecordMessage, Type

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .purchase_generator import PurchaseGenerator
from .utils import format_airbyte_time, now_millis


class ReviewGenerator:
    def __init__(self, stream_name: str, seed: int, parallelism: int) -> None:
        self.stream_name = stream_name
        self.seed = seed
        # The purchases pool workers always sit `parallelism` slots before the reviews pool workers in the global worker
        # identity counter, so seeding the inner generator with seed - parallelism makes its per-worker seed offset match
        # the purchases stream's and regenerates byte-identical purchase records.
        inner_seed = seed - parallelism if seed is not None else None
        self.purchase_generator = PurchaseGenerator("purchases", inner_seed)

    def prepare(self):
        """
        Note: the instances of the mimesis generators need to be global.
        See PurchaseGenerator.prepare for why.
        """

        self.purchase_generator.prepare()

    def generate(self, user_id: int) -> List[AirbyteMessageWithCachedJSON]:
        """
        Generate one review per purchase, regenerating the purchase records so that
        review.user_id/product_id always match the underlying purchase.
        """

        reviews: List[AirbyteMessageWithCachedJSON] = []
        purchases = self.purchase_generator.generate(user_id)

        # Review-only fields are seeded per user_id so they are deterministic for a
        # given seed regardless of which worker generates them or in what order.
        review_seed = self.seed + user_id if self.seed is not None else None
        numeric = Numeric(seed=review_seed)
        text = Text(locale=Locale.EN, seed=review_seed)

        for message in purchases:
            purchase = message.record.data
            base_date = purchase["purchased_at"] if purchase["purchased_at"] is not None else purchase["added_to_cart_at"]
            base_date = datetime.datetime.fromisoformat(base_date).replace(tzinfo=None)

            review = {
                "id": purchase["id"],
                "purchase_id": purchase["id"],
                "user_id": purchase["user_id"],
                "product_id": purchase["product_id"],
                "rating": numeric.integer_number(1, 5),
                "title": text.title(),
                "body": text.text(quantity=3),
                "created_at": format_airbyte_time(base_date + datetime.timedelta(days=numeric.integer_number(0, 30))),
                "updated_at": format_airbyte_time(datetime.datetime.now()),
            }

            record = AirbyteRecordMessage(stream=self.stream_name, data=review, emitted_at=now_millis())
            message = AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)
            reviews.append(message)

        return reviews

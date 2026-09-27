#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import List

from mimesis import Datetime, Numeric, Text
from mimesis.locales import Locale

from airbyte_cdk.models import AirbyteRecordMessage, Type

from . import purchase_generator
from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .purchase_generator import PurchaseGenerator
from .utils import format_airbyte_time, now_millis


class ReviewGenerator:
    def __init__(self, stream_name: str, seed: int) -> None:
        self.stream_name = stream_name
        self.seed = seed
        self.purchase_generator = PurchaseGenerator("purchases", seed)

    def prepare(self):
        """
        Note: the instances of the mimesis generators need to be global.
        See PurchaseGenerator.prepare for why.
        """

        self.purchase_generator.prepare()

    def purchases_for(self, user_id: int) -> List[AirbyteMessageWithCachedJSON]:
        """
        Regenerate the purchase set for a user with a per-user seed, so the review data
        is deterministic for a given seed regardless of worker/process allocation.
        """

        record_seed = self.seed + user_id if self.seed is not None else None
        purchase_generator.dt = Datetime(seed=record_seed)
        purchase_generator.numeric = Numeric(seed=record_seed)
        return self.purchase_generator.generate(user_id)

    def generate(self, user_id: int) -> List[AirbyteMessageWithCachedJSON]:
        """
        Generate one review per purchase. id/purchase_id/user_id match the purchases
        stream (the id scheme is RNG-independent), while product_id and the created_at
        base come from the regenerated purchase.
        """

        reviews: List[AirbyteMessageWithCachedJSON] = []
        purchases = self.purchases_for(user_id)

        record_seed = self.seed + user_id if self.seed is not None else None
        numeric = Numeric(seed=record_seed)
        text = Text(locale=Locale.EN, seed=record_seed)

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

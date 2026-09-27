#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from multiprocessing import current_process
from typing import List

from mimesis import Datetime, Numeric, Text

from airbyte_cdk.models import AirbyteRecordMessage, Type

from . import purchase_generator as purchase_generator_module
from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .purchase_generator import PurchaseGenerator
from .utils import format_airbyte_time, now_millis


class ReviewGenerator:
    def __init__(self, stream_name: str, seed: int) -> None:
        self.stream_name = stream_name
        self.seed = seed

    def prepare(self):
        """
        Note: the instances of the mimesis generators need to be global.
        See PurchaseGenerator.prepare for why.

        This also prepares a PurchaseGenerator in the same worker process, so that reviews can be generated
        one-per-purchase. The Purchases stream uses its own Pool, so its generator state is never touched here.
        """

        seed_with_offset = self.seed
        if self.seed is not None and len(current_process()._identity) > 0:
            seed_with_offset = self.seed + current_process()._identity[0]

        global dt
        global numeric
        global text
        global purchase_generator

        dt = Datetime(seed=seed_with_offset)
        numeric = Numeric(seed=seed_with_offset)
        text = Text(seed=seed_with_offset)

        purchase_generator = PurchaseGenerator("purchases", self.seed)
        purchase_generator.prepare()

    def generate(self, user_id: int) -> List[AirbyteMessageWithCachedJSON]:
        """
        Generates one review per purchase for the given user_id.
        When a seed is set, the generators are reseeded per user_id so that output is deterministic
        regardless of parallelism or which worker process happens to run this user_id.
        """

        if self.seed is not None:
            per_user_seed = self.seed + user_id
            dt.reseed(per_user_seed)
            numeric.reseed(per_user_seed)
            text.reseed(per_user_seed)
            purchase_generator_module.dt.reseed(per_user_seed)
            purchase_generator_module.numeric.reseed(per_user_seed)

        purchases = purchase_generator.generate(user_id)

        reviews: List[AirbyteMessageWithCachedJSON] = []
        for purchase_message in purchases:
            data = purchase_message.record.data

            # Anchor the review on the purchase date when the item was purchased; otherwise anchor on when it was
            # added to the cart (added_to_cart_at is never None). Either way, every purchase gets exactly one review.
            base = data["purchased_at"] if data["purchased_at"] is not None else data["added_to_cart_at"]
            base_dt = datetime.datetime.fromisoformat(base).replace(tzinfo=None)
            created_at = base_dt + datetime.timedelta(days=numeric.integer_number(0, 30))

            review = {
                "id": data["id"],
                "purchase_id": data["id"],
                "user_id": data["user_id"],
                "product_id": data["product_id"],
                "rating": numeric.integer_number(1, 5),
                "title": text.title(),
                "body": text.text(quantity=3),
                "created_at": format_airbyte_time(created_at),
                "updated_at": format_airbyte_time(datetime.datetime.now()),
            }

            record = AirbyteRecordMessage(stream=self.stream_name, data=review, emitted_at=now_millis())
            message = AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)
            reviews.append(message)

        return reviews

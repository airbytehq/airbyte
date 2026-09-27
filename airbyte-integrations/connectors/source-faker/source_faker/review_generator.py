#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from multiprocessing import current_process
from typing import List

from mimesis import Datetime, Numeric, Text

from airbyte_cdk.models import AirbyteRecordMessage, Type

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .utils import format_airbyte_time, now_millis


def purchase_ids_for_user(user_id: int) -> List[int]:
    """
    Replicates the purchase ID scheme from PurchaseGenerator.generate so that every
    review maps 1:1 to a purchase without sharing RNG state.
    """
    last_user_id_digit = int(repr(user_id)[-1])
    purchase_count = 1
    id_offset = 0
    if last_user_id_digit - 1 == 5:
        purchase_count = 0
    elif last_user_id_digit - 1 == 6:
        id_offset = 1
    elif last_user_id_digit - 1 == 7:
        id_offset = 1
        purchase_count = 2

    return [user_id + i + 1 - id_offset for i in range(purchase_count)]


class ReviewGenerator:
    def __init__(self, stream_name: str, seed: int) -> None:
        self.stream_name = stream_name
        self.seed = seed

    def prepare(self):
        """
        Note: the instances of the mimesis generators need to be global.
        Yes, they *should* be able to be instance variables on this class, which should only instantiated once-per-worker, but that's not quite the case:
        * relying only on prepare as a pool initializer fails because we are calling the parent process's method, not the fork
        * Calling prepare() as part of generate() (perhaps checking if self.person is set) and then `print(self, current_process()._identity, current_process().pid)` reveals multiple object IDs in the same process, resetting the internal random counters
        """

        seed_with_offset = self.seed
        if self.seed is not None and len(current_process()._identity) > 0:
            seed_with_offset = self.seed + current_process()._identity[0]

        global dt
        global numeric
        global text

        dt = Datetime(seed=seed_with_offset)
        numeric = Numeric(seed=seed_with_offset)
        text = Text(seed=seed_with_offset)

    def generate(self, user_id: int) -> List[AirbyteMessageWithCachedJSON]:
        """
        One review per purchase. Reviews are anchored on a deterministic purchase date
        derived from the same id scheme, since the purchases stream's RNG output is
        worker-allocation dependent.
        """
        if self.seed is not None:
            dt.reseed(self.seed + user_id)
            numeric.reseed(self.seed + user_id)
            text.reseed(self.seed + user_id)

        reviews: List[AirbyteMessageWithCachedJSON] = []
        for purchase_id in purchase_ids_for_user(user_id):
            time_a = dt.datetime()
            time_b = dt.datetime()
            purchase_created = time_a if time_a <= time_b else time_b
            purchased_at = purchase_created + datetime.timedelta(days=numeric.integer_number(0, 365))
            created_at = purchased_at + datetime.timedelta(days=numeric.integer_number(0, 30))

            review = {
                "id": purchase_id,
                "purchase_id": purchase_id,
                "user_id": user_id + 1,
                "product_id": numeric.integer_number(1, 100),
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

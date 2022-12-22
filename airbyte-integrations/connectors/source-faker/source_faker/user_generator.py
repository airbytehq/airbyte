#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from multiprocessing import current_process

from airbyte_cdk.models import AirbyteRecordMessage, Type
from mimesis import Datetime, Person
from mimesis.locales import Locale

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .utils import format_airbyte_time, now_millis


class UserGenerator:
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

        global person
        global dt

        person = Person(locale=Locale.EN, seed=seed_with_offset)
        dt = Datetime(seed=seed_with_offset)

    def generate(self, user_id: int):
        time_a = dt.datetime()
        time_b = dt.datetime()

        # faker doesn't always produce unique email addresses, so to enforce uniqueness, we will append the user_id to the prefix
        email_parts = person.email().split("@")
        email = f"{email_parts[0]}+{user_id + 1}@{email_parts[1]}"

        profile = {
            "id": user_id + 1,
            "created_at": format_airbyte_time(time_a if time_a <= time_b else time_b),
            "updated_at": format_airbyte_time(time_a if time_a > time_b else time_b),
            "name": person.name(),
            "title": person.title(),
            "age": person.age(),
            "email": email,
            "telephone": person.telephone(),
            "gender": person.gender(),
            "language": person.language(),
            "academic_degree": person.academic_degree(),
            "nationality": person.nationality(),
            "occupation": person.occupation(),
            "height": person.height(),
            "blood_type": person.blood_type(),
            "weight": person.weight(),
        }

        while not profile["created_at"]:
            profile["created_at"] = format_airbyte_time(dt.datetime())

        if not profile["updated_at"]:
            profile["updated_at"] = profile["created_at"] + 1

        record = AirbyteRecordMessage(stream=self.stream_name, data=profile, emitted_at=now_millis())
        return AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)

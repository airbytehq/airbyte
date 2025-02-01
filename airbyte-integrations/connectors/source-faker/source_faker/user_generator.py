#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from multiprocessing import current_process

from mimesis import Address, Datetime, Person
from mimesis.locales import Locale

from airbyte_cdk.models import AirbyteRecordMessage, Type
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .utils import format_airbyte_time, now_millis

# Global variables for mimesis generators
from typing import cast

person: Person | None = None
address: Address | None = None
dt: Datetime | None = None


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
        global address
        global dt

        person = Person(locale=Locale.EN, seed=seed_with_offset)
        address = Address(locale=Locale.EN, seed=seed_with_offset)
        dt = Datetime(seed=seed_with_offset)

    def generate(self, user_id: int):
        try:
            if not all([person, address, dt]):
                self.prepare()
            
            # After prepare(), these should never be None
            person_gen = cast(Person, person)
            address_gen = cast(Address, address)
            dt_gen = cast(Datetime, dt)

            # faker doesn't always produce unique email addresses, so to enforce uniqueness, we will append the user_id to the prefix
            email_parts = person_gen.email().split("@")
            email = f"{email_parts[0]}+{user_id + 1}@{email_parts[1]}"

            profile = {
                "id": user_id + 1,
                "created_at": format_airbyte_time(dt_gen.datetime()),
                "updated_at": format_airbyte_time(datetime.datetime.now()),
                "name": person_gen.name(),
                "title": person_gen.title(),
                "age": person_gen.age(),
                "email": email,
                "telephone": person_gen.telephone(),
                "gender": person_gen.gender(),
                "language": person_gen.language(),
                "academic_degree": person_gen.academic_degree(),
                "nationality": person_gen.nationality(),
                "occupation": person_gen.occupation(),
                "height": person_gen.height(),
                "blood_type": person_gen.blood_type(),
                "weight": person_gen.weight(),
                "address": {
                    "street_number": address_gen.street_number(),
                    "street_name": address_gen.street_name(),
                    "city": address_gen.city(),
                    "state": address_gen.state(),
                    "province": address_gen.province(),
                    "postal_code": address_gen.postal_code(),
                    "country_code": address_gen.country_code(),
                },
            }

            while not profile["created_at"]:
                profile["created_at"] = format_airbyte_time(dt_gen.datetime())

            record = AirbyteRecordMessage(stream=self.stream_name, data=profile, emitted_at=now_millis())
            return AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)
        except Exception as e:
            error_msg = f"Error generating user record {user_id}: {str(e)}"
            raise AirbyteTracedException(
                message=error_msg,
                internal_message=error_msg,
                failure_type=FailureType.system_error,
                exception=e
            )

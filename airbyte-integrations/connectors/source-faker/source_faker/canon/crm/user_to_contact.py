# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from source_faker.canon.canonical_stream import TransformFunction
from source_faker.canon.crm.contact import Address, Contact, Email, PhoneNumber

from airbyte_cdk.sources.types import Record


class UserToContact(TransformFunction[Contact]):
    def __call__(self, record: Record) -> Record:
        return Record(
            data=Contact(
                id=str(record["id"]),
                first_name=record["name"],
                last_name=None,
                addresses=[
                    Address(
                        street_number=record["address"]["street_number"],
                        street_name=record["address"]["street_name"],
                        city=record["address"]["city"],
                        state=record["address"]["state"],
                        postal_code=record["address"]["postal_code"],
                    )
                ],
                emails=[Email(email=record["email"], email_type="PERSONAL")],
                phones=[PhoneNumber(phone_number=record["telephone"], phone_type="PERSONAL")],
                account_id=None,
                created_at=record["created_at"],
                updated_at=record["updated_at"],
                deleted_at=None,
                # The address should probbaly also be in additional_properties because we're dropping the country code...
                additional_properties={
                    k: v for k, v in record.items() if k not in ["id", "name", "telephone", "created_at", "updated_at", "email"]
                },
            ).model_dump(),
            stream_name=Contact.stream_name(),
            associated_slice=record.associated_slice,
        )

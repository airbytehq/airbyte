# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from source_faker.canon.canonical_model import CanonicalModel, TimestampedModel


AddressType = Literal["BILLING", "SHIPPING", "OTHER"]
EmailType = Literal["WORK", "PERSONAL", "OTHER"]
PhoneType = Literal["WORK", "PERSONAL", "OTHER"]


class Address(BaseModel):
    street_1: str | None = Field(default=None, description="The first line of the address")
    street_2: str | None = Field(default=None, description="The second line of the address")
    city: str | None = Field(default=None, description="The city of the address")
    state: str | None = Field(default=None, description="The state of the address")
    zip: str | None = Field(default=None, description="The zip code of the address")
    country: str | None = Field(default=None, description="The country of the address")
    address_type: AddressType | None = Field(default=None, description="The type of address. Either 'BILLING', 'SHIPPING', or 'OTHER'")


class Email(BaseModel):
    email: str = Field(description="The email address")
    email_type: EmailType = Field(description="The type of email. Either 'WORK', 'PERSONAL', or 'OTHER'")


class PhoneNumber(BaseModel):
    phone_number: str = Field(description="The phone number")
    phone_type: PhoneType = Field(description="The type of phone. Either 'WORK', 'PERSONAL', or 'OTHER'")


class Contact(CanonicalModel):
    first_name: str | None = Field(description="The first name of the contact")
    last_name: str | None = Field(description="The last name of the contact")
    addresses: list[Address] = Field(description="The addresses of the contact")
    emails: list[Email] = Field(description="The emails of the contact")
    phones: list[PhoneNumber] = Field(description="The phones of the contact")
    account_id: str | None = Field(description="The account id of the contact")

    @classmethod
    def stream_name(cls) -> str:
        return "crm_contacts"

#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Any, List, MutableMapping, Type

from pydantic import BaseModel


class BaseSchemaModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

        @classmethod
        def schema_extra(cls, schema: MutableMapping[str, Any], model: Type["BaseModel"]) -> None:
            # Modify pydantic generated jsonschema.
            # Remove "title" and "description" fields to reduce size.
            schema.pop("title", None)
            schema.pop("description", None)
            # Remove required section so any missing attribute from API wont break object validation.
            schema.pop("required", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                prop.pop("description", None)
                allow_none = model.__fields__[name].allow_none
                # Pydantic doesnt treat Union[None, Any] type correctly when
                # generation jsonschema so we cant set field as nullable (i.e.
                # field that can have either null and non-null values),
                # generate this jsonschema value manually.
                if "type" in prop:
                    if allow_none:
                        prop["type"] = ["null", prop["type"]]


class Application(BaseSchemaModel):
    id: str
    type: str
    candidateId: str = None
    opportunityId: str
    posting: str = None
    postingHiringManager: str = None
    postingOwner: str = None
    name: str = None
    company: str = None
    phone: dict = None
    email: str = None
    links: List[str]
    comments: str = None
    user: str = None
    customQuestions: List[dict]
    createdAt: int
    archived: dict = None
    requisitionForHire: dict = None


class Interview(BaseSchemaModel):
    id: str
    panel: str = None
    subject: str = None
    note: str = None
    interviewers: List[dict]
    timezone: str = None
    createdAt: int
    date: int = None
    duration: int = None
    location: str = None
    feedbackTemplate: str = None
    feedbackForms: List[str]
    feedbackReminder: str = None
    user: str = None
    stage: str = None
    canceledAt: int = None
    postings: List[str]
    gcalEventUrl: str = None


class Note(BaseSchemaModel):
    id: str
    text: str = None
    fields: List[dict]
    user: str = None
    secret: bool = None
    completedAt: int = None
    deletedAt: int = None
    createdAt: int


class Offer(BaseSchemaModel):
    id: str
    posting: str = None
    createdAt: int
    status: str = None
    creator: str = None
    fields: List[dict]
    signatures: dict
    approved: str = None
    approvedAt: int = None
    sentAt: int = None
    sentDocument: dict = None
    signedDocument: dict = None


class Opportunity(BaseSchemaModel):
    id: str
    name: str = None
    contact: str = None
    headline: str = None
    stage: str = None
    confidentiality: str = None
    location: str = None
    phones: List[dict]
    emails: List[str]
    links: List[str]
    archived: dict = None
    tags: List[str]
    sources: List[str]
    stageChanges: List[dict]
    origin: str = None
    sourcedBy: str = None
    owner: str = None
    followers: List[str]
    applications: List[str]
    createdAt: int
    updatedAt: int
    lastInteractionAt: int = None
    lastAdvancedAt: int = None
    snoozedUntil: int = None
    urls: dict = None
    resume: str = None
    dataProtection: dict = None
    isAnonymized: bool


class Referral(BaseSchemaModel):
    id: str
    type: str = None
    text: str = None
    instructions: str = None
    fields: List[dict]
    baseTemplateId: str = None
    user: str = None
    referrer: str = None
    stage: str = None
    createdAt: int
    completedAt: int = None


class User(BaseSchemaModel):
    id: str
    name: str = None
    username: str = None
    email: str = None
    accessRole: str = None
    photo: str = None
    createdAt: int
    deactivatedAt: int = None
    externalDirectoryId: str = None
    linkedContactIds: List[str] = None

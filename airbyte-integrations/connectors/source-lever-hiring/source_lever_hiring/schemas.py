#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, MutableMapping, Optional, Type

import pydantic
from pydantic import BaseModel
from pydantic.typing import resolve_annotations


class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        """
        Iterate through fields and wrap then with typing.Optional type.
        """
        annotations = resolve_annotations(namespaces.get("__annotations__", {}), namespaces.get("__module__", None))
        for base in bases:
            annotations = {**annotations, **getattr(base, "__annotations__", {})}
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class BaseSchemaModel(BaseModel, metaclass=AllOptional):
    class Config:
        arbitrary_types_allowed = True

        @classmethod
        def schema_extra(cls, schema: MutableMapping[str, Any], model: Type["BaseModel"]) -> None:
            # Remove auto generated "title" and "description" fields, because they do not carry absolutely any payload.
            schema.pop("title", None)
            schema.pop("description", None)
            # Remove required section so any missing attribute from API wont break object validation.
            schema.pop("required", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                prop.pop("description", None)
                allow_none = model.__fields__[name].allow_none
                if allow_none:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]


class Application(BaseSchemaModel):
    id: str
    type: str
    candidateId: str
    opportunityId: str
    posting: str
    postingHiringManager: str
    postingOwner: str
    name: str
    company: str
    phone: dict
    email: str
    links: List[str]
    comments: str
    user: str
    customQuestions: List[dict]
    createdAt: int
    archived: dict
    requisitionForHire: dict


class Interview(BaseSchemaModel):
    id: str
    panel: str
    subject: str
    note: str
    interviewers: List[dict]
    timezone: str
    createdAt: int
    date: int
    duration: int
    location: str
    feedbackTemplate: str
    feedbackForms: List[str]
    feedbackReminder: str
    user: str
    stage: str
    canceledAt: int
    postings: List[str]
    gcalEventUrl: str


class Note(BaseSchemaModel):
    id: str
    text: str
    fields: List[dict]
    user: str
    secret: bool
    completedAt: int
    deletedAt: int
    createdAt: int


class Offer(BaseSchemaModel):
    id: str
    posting: str
    createdAt: int
    status: str
    creator: str
    fields: List[dict]
    signatures: dict
    approved: str
    approvedAt: int
    sentAt: int
    sentDocument: dict
    signedDocument: dict


class Opportunity(BaseSchemaModel):
    id: str
    name: str
    contact: str
    headline: str
    stage: str
    confidentiality: str
    location: str
    phones: List[dict]
    emails: List[str]
    links: List[str]
    archived: dict
    tags: List[str]
    sources: List[str]
    stageChanges: List[dict]
    origin: str
    sourcedBy: str
    owner: str
    followers: List[str]
    applications: List[str]
    createdAt: int
    updatedAt: int
    lastInteractionAt: int
    lastAdvancedAt: int
    snoozedUntil: int
    urls: dict
    resume: str
    dataProtection: dict
    isAnonymized: bool


class Referral(BaseSchemaModel):
    id: str
    type: str
    text: str
    instructions: str
    fields: List[dict]
    baseTemplateId: str
    user: str
    referrer: str
    stage: str
    createdAt: int
    completedAt: int


class User(BaseSchemaModel):
    id: str
    name: str
    username: str
    email: str
    accessRole: str
    photo: str
    createdAt: int
    deactivatedAt: int
    externalDirectoryId: str
    linkedContactIds: List[str]

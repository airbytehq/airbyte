from typing import Any, Mapping, List
from abc import ABC, abstractmethod

class BaseIntercomModel(ABC):
    @property
    @abstractmethod
    def path(self) -> str:
        pass

    @property
    @abstractmethod
    def default_attributes(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def excluded_attributes(self) -> List[str]:
        pass

    @abstractmethod
    def upsert(self):
        pass

    # @abstractmethod
    # def delete(self):
    #     pass


class ContactModel(BaseIntercomModel):
    @property
    def path(self) -> str:
        return 'contacts'

    # contact request body parameters from https://developers.intercom.com/intercom-api-reference/reference#create-contact
    @property
    def default_attributes(self) -> List[str]:
        return [
            'role',
            'external_id',
            'email',
            'phone',
            'name',
            'avatar',
            'signed_up_at',
            'last_seen_at',
            'owner_id',
            'unsubscribed_from_emails',
        ]

    @property
    def excluded_attributes(self) -> List[str]:
        return []

    def upsert(
        self, 
        email: str
    ):
        try:
            # create user
            user_response = self.send_request(
                endpoint='contacts',
                json={
                    "role": "user",
                    "email": email
                }
            )
        except requests.exceptions.HTTPError:
            # search for user
            user_response = self.send_request(
                endpoint='contacts/search',
                json={
                    "query":  {
                        "field": "email",
                        "operator": "=",
                        "value": email
                    }
                }
            )


class CompanyModel(BaseIntercomModel):
    @property
    def path(self) -> str:
        return 'companies'

    # company request body parameters from https://developers.intercom.com/intercom-api-reference/reference#create-or-update-company
    @property
    def default_attributes(self) -> List[str]:
        return [
            'remote_created_at',
            'company_id',
            'name',
            'monthly_spend',
            'plan',
            'size',
            'website',
            'industry'
        ]
    
    @property
    def excluded_attributes(self) -> List[str]:
        return ['user_email']

    @property
    def user_key(self):
        return 'user_email'

    def upsert(
        self, 
        email: str
    ):
        airbyte_json = self.format_json_data(record)
        return self.send_request(
            endpoint='companies',
            json=airbyte_json
        )

    def attach_company_to_user(
        self
    ):
        return self.send_request(
            endpoint=f'contacts/{user_id}/companies',
            json={"id": company_id}
        )

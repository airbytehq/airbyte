#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Tuple, Union
import logging
import requests

class NGPVANClient:
    base_uri = "https://api.securevan.com/v4/"

    def __init__(self,
                 local_test: bool = True,
                 bulk_import_type: str = None,
                 van_api_key: str = None,
                 gcs_bucket: str = None,
                 service_account_key: str = None
                 ):

        self.local_test = local_test
        self.bulk_import_type = bulk_import_type
        self.van_api_key = van_api_key
        self.gcs_bucket = gcs_bucket
        self.service_account_key = service_account_key
        self.auth = ('default',
                     van_api_key + '|1')  # adding '|1' authorizes for MyCampaign; we can parameterize this when we need to interact with MyVoters

    def _request(self, auth: tuple, method: str, endpoint: str = None, params: Mapping[str, Any] = None, json: Mapping[str, Any] = None
                 ) -> requests.Response:
        url = self.base_uri + (endpoint or "")
        response = requests.request(method=method, params=params, url=url, json=json, auth=self.auth)
        response.raise_for_status()

        return response

    def get_bulk_import_job_status(self, job_id: str) -> requests.Response:
        """Returns status of bulk import job"""
        endpoint="bulkImportJobs/"+job_id

        return self._request(method="GET", auth=self.auth, endpoint=endpoint).json()

    def bulk_upsert_contacts(self, fileName: str, columns: list, sourceUrl: str) -> requests.Response:
        """
        Bulk create or update contact records.

        **Table Fields**

        Field names must match these values exactly. (TODO() make this more flexible)
        No fields are strictly required to run the bulk import. If VanID is not provided, VAN will attempt to match with an existing record, and will create a new one if none is found (proceed with caution).

        * DisplayAsEntered
        * AddressLine1
        * AddressLine2
        * AddressLine3
        * CellPhone
        * CellPhoneCountryCode
        * City
        * ContactModeID
        * CountryCode
        * DOB
        * Email
        * EmployerName
        * AdditionalEnvelopeName
        * FormalEnvelopeName
        * EnvelopeName
        * FirstName
        * Phone
        * PhoneCountryCode
        * IsInFileMatchingEnabled
        * LastName
        * External_3ID
        * MiddleName
        * External_81ID
        * OccupationName
        * OrganizationContactCommonName
        * OrganizationContactOfficialName
        * OtherEmail
        * Title
        * ProfessionalSuffix
        * AdditionalSalutation
        * FormalSalutation
        * Salutation
        * Sex
        * StateOrProvince
        * Suffix
        * VanID
        * WorkEmail
        * WorkPhone
        * WorkPhoneCountryCode
        * ZipOrPostal
        * Action
        * DoNotUpdateBest
        * SkipEmailSubscriptionUpdate

        `Returns:`
            int
                The bulk import job id
        """

        endpoint = "bulkImportJobs"
        description = "Create Or Update Contact Records"
        resource_type = "Contacts"

        payload = {"description": description,
                   "file": {
                       "columnDelimiter": 'csv',
                       "columns": [{'name': c} for c in columns],
                       "fileName": fileName,
                       "hasHeader": "True",
                       "hasQuotes": "True",
                       "sourceUrl": sourceUrl},
                   "actions": [{"resultFileSizeKbLimit": 5000,
                                "resourceType": resource_type,
                                "actionType": "loadMappedFile",
                                "mappingTypes": [{'name': 'CreateOrUpdateContact'}]}]
                   }

        logging.info(f"Sending POST request to VAN to bulk upsert contacts")

        return self._request(method="POST", endpoint=endpoint, auth=self.auth, json=payload)

    def bulk_apply_activist_codes(self, fileName: str, columns: list, sourceUrl: str) -> requests.Response:
        """
        Bulk import job history: https://app.ngpvan.com/BulkUploadBatchesList.aspx

        Bulk apply activist codes.

        The table may include the following columns.
        Required columns: `VanID`, `ActivistCodeID`

        * VanID (REQUIRED)
        * ActivistCodeID (REQUIRED)
        * CanvassedBy
        * DateCanvassed
        * ContactTypeID

        `Returns:`
            int
                The bulk import job id
        """

        endpoint = "bulkImportJobs"
        description = "Activist Code Upload"
        resource_type = "ContactsActivistCodes"

        payload = {"description": description,
                   "file": {
                       "columnDelimiter": 'csv',
                       "columns": [{'name': c} for c in columns],
                       "fileName": fileName,
                       "hasHeader": "True",
                       "hasQuotes": "True",
                       "sourceUrl": sourceUrl},
                   "actions": [{"resultFileSizeKbLimit": 5000,
                                "resourceType": resource_type,
                                "actionType": "loadMappedFile",
                                "mappingTypes": [{'name': 'ActivistCode'}]}]
                   }

        logging.info(f"Sending POST request to VAN to bulk upsert contacts")

        return self._request(method="POST", endpoint=endpoint, auth=self.auth, json=payload)

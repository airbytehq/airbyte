#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Tuple, Union

import requests


class NGPVANClient:
    base_uri = "https://api.securevan.com/v4/"

    def __init__(self, local_test: bool = True, van_api_key: str = None, service_account_key: str = None):
        self.local_test = local_test
        self.van_api_key = van_api_key
        self.service_account_key = service_account_key
        self.auth = ('default',
                     van_api_key + '|1')  # adding '|1' authorizes for MyCampaign; we can parameterize this when we need to interact with MyVoters

    def _request(self, auth: tuple, method: str, endpoint: str = None, params: Mapping[str, Any] = None, json: Mapping[str, Any] = None
                 ) -> requests.Response:
        url = self.base_uri + (endpoint or "")
        response = requests.request(method=method, params=params, url=url, json=json, auth=self.auth)
        response.raise_for_status()

        return response

    def get_mappings(self) -> requests.Response:
        """Returns json object containing bulk import mapping types (this might not actually be useful)"""
        endpoint = "bulkImportMappingTypes"
        return self._request(method="GET", auth=self.auth, endpoint=endpoint).json()

    def bulk_upsert_contacts(self, sourceUrl: str) -> requests.Response:
        """
        Bulk create or update contact records. Provide a Parsons table of contact data to
        create or update records.

        .. note::
            * The first column of the table must be VANID.
            * The other columns can be a combination of the columns listed below.
              The valid column names also accept permutations with underscores, spaces
              and capitalization (e.g. ``phonenumber`` = ``Phone_Number``).

        **Table Fields**

        .. list-table::
            :widths: 500 100 10
            :header-rows: 1

            * - Column
              - Valid Column Names
              - Notes
            * - VANID
              - ``vanid``
              -
            * - Voter VAN ID
              - ``votervanid``
              - The contact's MyVoters VANID
            * - External ID
              - ``externalid``, ``id``, ``pk``, ``voterbaseid``
              - An external id to be stored.
            * - **PII**
              -
              -
            * - First Name
              - ``fn``, ``firstname``, ``last``
              -
            * - Middle Name
              - ``mn``, ``middlename``, ``middle``
              -
            * - Last Name
              - ``ln``, ``lastname``, ``last``
              -
            * - Date of Birth
              - ``dob``, ``dateofbirth`` ``birthdate``
              - What type of thing does this need?
            * - Sex
              - ``sex``, ``gender``
              -
            * - **Physical Address**
              -
              -
            * - Address Line 1
              - ``addressline1``, ``address1``, ``address``
              -
            * - Address Line 2
              - ``addressline2``, ``address2``
              -
            * - Address Line 3
              - ``addressline3``, ``address3``
              -
            * - City
              - ``city``
              -
            * - State Or Province
              - ``state``, ``st``, ``stateorprovince``
              -
            * - Country Code
              - ``countrycode``, ``country``
              - A valid two character country code (e.g. ``US``)
            * - Display As Entered
              - ``displayasentered``
              - Required values are ``Y`` and ``N``. Determines if the address is
                processed through address correction.
            * - **Phones**
              -
              -
            * - Cell Phone
              - ``cellphone``, ``cell``
              -
            * - Cell Phone Country Code
              - ``cellcountrycode``, ``cellphonecountrycode``
              - A valid two digit country code (e.g. ``01``)
            * - Home Phone
              - ``homephone``, ``home``, ``phone``
              -
            * - Home Phone Country Code
              - ``homecountrycode``, ``homephonecountrycode``
              -
            * - **Email**
              -
              -
            * - Email
              - ``email``, ``emailaddress``
              -

        `Args:`
            table: Parsons table
              A Parsons table.
            url_type: str
              The cloud file storage to use to post the file. Currently only ``S3``.
            results_fields: list
              A list of fields to include in the results file.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
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
                       "fileName": 'test_upsert_contacts.csv',
                       "hasHeader": "True",
                       "hasQuotes": "True",
                       "sourceUrl": sourceUrl},
                   "actions": [{"resultFileSizeKbLimit": 5000,
                                "resourceType": resource_type,
                                "actionType": "loadMappedFile",
                                "mappingTypes": [{'name': 'CreateOrUpdateContact'}]}]
                   }

        return self._request(method="POST", endpoint=endpoint, auth=self.auth, json=payload)

    def bulk_apply_activist_codes(self, sourceUrl: str) -> requests.Response:
        """
        TODO: need to figure out how the mapping stuff works. This successfully sends a file to the VAN API but the bulk import fails.
        Bulk import job history: https://app.ngpvan.com/BulkUploadBatchesList.aspx

        Bulk apply activist codes.

        The table may include the following columns. The first column
        must be ``vanid``.

        .. list-table::
            :widths: 25 25 50
            :header-rows: 1

            * - Column Name
              - Required
              - Description
            * - ``vanid``
              - Yes
              - A valid VANID primary key
            * - ``activistcodeid``
              - Yes
              - A valid activist code id
            * - ``datecanvassed``
              - No
              - An ISO formatted date
            * - ``contacttypeid``
              - No
              - The method of contact.

        `Args:`
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`Cloud Storage <cloud-storage>` for more details.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
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
                       "fileName": 'output_airbyte.csv',
                       "hasHeader": "True",
                       "hasQuotes": "True",
                       "sourceUrl": sourceUrl},
                   "actions": [{"resultFileSizeKbLimit": 5000,
                                "resourceType": resource_type,
                                "actionType": "loadMappedFile",
                                "mappingTypes": [{'name': 'ActivistCode'}]}]
                   }

        return self._request(method="POST", endpoint=endpoint, auth=self.auth, json=payload)

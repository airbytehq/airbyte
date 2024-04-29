# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from suds.transport import Reply, Request
from suds.transport.https import HttpAuthenticated

SEARCH_ACCOUNTS_RESPONSE = b"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Header>
        <h:TrackingId xmlns:h="https://bingads.microsoft.com/Customer/v13">6f0a329e-4cb4-4c79-9c08-2dfe601ba05a
        </h:TrackingId>
    </s:Header>
    <s:Body>
        <SearchAccountsResponse xmlns="https://bingads.microsoft.com/Customer/v13">
            <Accounts xmlns:a="https://bingads.microsoft.com/Customer/v13/Entities"
                      xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                <a:AdvertiserAccount>
                    <a:BillToCustomerId>251186883</a:BillToCustomerId>
                    <a:CurrencyCode>USD</a:CurrencyCode>
                    <a:AccountFinancialStatus>ClearFinancialStatus</a:AccountFinancialStatus>
                    <a:Id>180535609</a:Id>
                    <a:Language>English</a:Language>
                    <a:LastModifiedByUserId>0</a:LastModifiedByUserId>
                    <a:LastModifiedTime>2023-08-11T08:24:26.603</a:LastModifiedTime>
                    <a:Name>DEMO-ACCOUNT</a:Name>
                    <a:Number>F149W3B6</a:Number>
                    <a:ParentCustomerId>251186883</a:ParentCustomerId>
                    <a:PaymentMethodId i:nil="true"/>
                    <a:PaymentMethodType i:nil="true"/>
                    <a:PrimaryUserId>138225488</a:PrimaryUserId>
                    <a:AccountLifeCycleStatus>Pause</a:AccountLifeCycleStatus>
                    <a:TimeStamp>AAAAAH10c1A=</a:TimeStamp>
                    <a:TimeZone>Santiago</a:TimeZone>
                    <a:PauseReason>2</a:PauseReason>
                    <a:ForwardCompatibilityMap i:nil="true"
                                               xmlns:b="http://schemas.datacontract.org/2004/07/System.Collections.Generic"/>
                    <a:LinkedAgencies/>
                    <a:SalesHouseCustomerId i:nil="true"/>
                    <a:TaxInformation xmlns:b="http://schemas.datacontract.org/2004/07/System.Collections.Generic"/>
                    <a:BackUpPaymentInstrumentId i:nil="true"/>
                    <a:BillingThresholdAmount i:nil="true"/>
                    <a:BusinessAddress>
                        <a:City>San Francisco</a:City>
                        <a:CountryCode>US</a:CountryCode>
                        <a:Id>149694999</a:Id>
                        <a:Line1>350 29th avenue</a:Line1>
                        <a:Line2 i:nil="true"/>
                        <a:Line3 i:nil="true"/>
                        <a:Line4 i:nil="true"/>
                        <a:PostalCode>94121</a:PostalCode>
                        <a:StateOrProvince>CA</a:StateOrProvince>
                        <a:TimeStamp i:nil="true"/>
                        <a:BusinessName>Daxtarity Inc.</a:BusinessName>
                    </a:BusinessAddress>
                    <a:AutoTagType>Inactive</a:AutoTagType>
                    <a:SoldToPaymentInstrumentId i:nil="true"/>
                    <a:TaxCertificate i:nil="false">
                        <a:TaxCertificateBlobContainerName i:nil="false">Test Container Name</a:TaxCertificateBlobContainerName>
                        <a:TaxCertificates xmlns:a="http://schemas.datacontract.org/2004/07/System.Collections.Generic" i:nil="false">
                          <a:KeyValuePairOfstringbase64Binary>
                            <a:key i:nil="false">test_key</a:key>
                            <a:value i:nil="false">test_value</a:value>
                          </a:KeyValuePairOfstringbase64Binary>
                        </a:TaxCertificates>
                        <a:Status i:nil="false">Active</a:Status>
                    </a:TaxCertificate>
                    <a:AccountMode>Expert</a:AccountMode>
                </a:AdvertiserAccount>
            </Accounts>
        </SearchAccountsResponse>
    </s:Body>
</s:Envelope>
"""

GET_USER_RESPONSE = b"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Header xmlns="https://bingads.microsoft.com/Customer/v13">
    <TrackingId d3p1:nil="false" xmlns:d3p1="http://www.w3.org/2001/XMLSchema-instance">762354725472</TrackingId>
  </s:Header>
  <s:Body>
    <GetUserResponse xmlns="https://bingads.microsoft.com/Customer/v13">
      <User xmlns:e227="https://bingads.microsoft.com/Customer/v13/Entities" d4p1:nil="false" xmlns:d4p1="http://www.w3.org/2001/XMLSchema-instance">
        <e227:ContactInfo d4p1:nil="false">
          <e227:Address d4p1:nil="false">
            <e227:City d4p1:nil="false">City</e227:City>
            <e227:CountryCode d4p1:nil="false">USD</e227:CountryCode>
            <e227:Id d4p1:nil="false">12345678</e227:Id>
            <e227:Line1 d4p1:nil="false">Test Line</e227:Line1>
            <e227:Line2 d4p1:nil="false">Test Line</e227:Line2>
            <e227:Line3 d4p1:nil="false">Test Line</e227:Line3>
            <e227:Line4 d4p1:nil="false">Test Line</e227:Line4>
            <e227:PostalCode d4p1:nil="false">0671</e227:PostalCode>
            <e227:StateOrProvince d4p1:nil="false">State</e227:StateOrProvince>
            <e227:TimeStamp d4p1:nil="false">12327485</e227:TimeStamp>
            <e227:BusinessName d4p1:nil="false">Test</e227:BusinessName>
          </e227:Address>
          <e227:ContactByPhone d4p1:nil="false">50005</e227:ContactByPhone>
          <e227:ContactByPostalMail d4p1:nil="false">7365</e227:ContactByPostalMail>
          <e227:Email d4p1:nil="false">test@mail.com</e227:Email>
          <e227:EmailFormat d4p1:nil="false">test</e227:EmailFormat>
          <e227:Fax d4p1:nil="false">73456-343</e227:Fax>
          <e227:HomePhone d4p1:nil="false">83563</e227:HomePhone>
          <e227:Id d4p1:nil="false">1232346573</e227:Id>
          <e227:Mobile d4p1:nil="false">736537</e227:Mobile>
          <e227:Phone1 d4p1:nil="false">2645</e227:Phone1>
          <e227:Phone2 d4p1:nil="false">45353</e227:Phone2>
        </e227:ContactInfo>
        <e227:CustomerId d4p1:nil="false">234627</e227:CustomerId>
        <e227:Id d4p1:nil="false">276342574</e227:Id>
        <e227:JobTitle d4p1:nil="false">Title Job</e227:JobTitle>
        <e227:LastModifiedByUserId d4p1:nil="false">234722342</e227:LastModifiedByUserId>
        <e227:LastModifiedTime d4p1:nil="false">2024-01-01T01:01:10.327</e227:LastModifiedTime>
        <e227:Lcid d4p1:nil="false">827462346</e227:Lcid>
        <e227:Name d4p1:nil="false">
          <e227:FirstName d4p1:nil="false">Name First</e227:FirstName>
          <e227:LastName d4p1:nil="false">Name Last</e227:LastName>
          <e227:MiddleInitial d4p1:nil="false">Test</e227:MiddleInitial>
        </e227:Name>
        <e227:Password d4p1:nil="false">test</e227:Password>
        <e227:SecretAnswer d4p1:nil="false">test</e227:SecretAnswer>
        <e227:SecretQuestion>test?</e227:SecretQuestion>
        <e227:UserLifeCycleStatus d4p1:nil="false">test</e227:UserLifeCycleStatus>
        <e227:TimeStamp d4p1:nil="false">2736452</e227:TimeStamp>
        <e227:UserName d4p1:nil="false">test</e227:UserName>
        <e227:ForwardCompatibilityMap xmlns:e228="http://schemas.datacontract.org/2004/07/System.Collections.Generic" d4p1:nil="false">
          <e228:KeyValuePairOfstringstring>
            <e228:key d4p1:nil="false">key</e228:key>
            <e228:value d4p1:nil="false">value</e228:value>
          </e228:KeyValuePairOfstringstring>
        </e227:ForwardCompatibilityMap>
        <e227:AuthenticationToken d4p1:nil="false">token</e227:AuthenticationToken>
      </User>
      <CustomerRoles xmlns:e229="https://bingads.microsoft.com/Customer/v13/Entities" d4p1:nil="false" xmlns:d4p1="http://www.w3.org/2001/XMLSchema-instance">
        <e229:CustomerRole>
          <e229:RoleId>8324628</e229:RoleId>
          <e229:CustomerId>726542</e229:CustomerId>
          <e229:AccountIds d4p1:nil="false" xmlns:a1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
            <a1:long>180535609</a1:long>
          </e229:AccountIds>
          <e229:LinkedAccountIds d4p1:nil="false" xmlns:a1="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
            <a1:long>180535609</a1:long>
          </e229:LinkedAccountIds>
          <e229:CustomerLinkPermission d4p1:nil="false">http://link</e229:CustomerLinkPermission>
        </e229:CustomerRole>
      </CustomerRoles>
    </GetUserResponse>
  </s:Body>
</s:Envelope>
"""


def mock_http_authenticated_send(transport: HttpAuthenticated, request: Request) -> Reply:
    if request.headers.get("SOAPAction").decode() == '"GetUser"':
        return Reply(code=200, headers={}, message=GET_USER_RESPONSE)

    if request.headers.get("SOAPAction").decode() == '"SearchAccounts"':
        return Reply(code=200, headers={}, message=SEARCH_ACCOUNTS_RESPONSE)

    raise Exception(f"Unexpected SOAPAction provided for mock SOAP client: {request.headers.get('SOAPAction').decode()}")

# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

AD_ACC_DATA = b"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
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
                    <a:AccountMode>Expert</a:AccountMode>
                </a:AdvertiserAccount>
            </Accounts>
        </SearchAccountsResponse>
    </s:Body>
</s:Envelope>
"""

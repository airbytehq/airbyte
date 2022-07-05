/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;

public class HubspotOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new HubspotOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://app.hubspot.com/oauth/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&scopes=crm.schemas.contacts.read&optional_scopes=content+crm.schemas.deals.read+crm.objects.owners.read+forms+tickets+e-commerce+crm.objects.companies.read+crm.lists.read+crm.objects.deals.read+crm.objects.contacts.read+crm.schemas.companies.read+files+forms-uploaded-files+files.ui_hidden.read+crm.objects.feedback_submissions.read+sales-email-read+automation";
  }

}

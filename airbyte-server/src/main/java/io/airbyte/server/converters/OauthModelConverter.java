/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.AdvancedAuth;
import io.airbyte.api.model.AdvancedAuth.AuthFlowTypeEnum;
import io.airbyte.api.model.AuthSpecification;
import io.airbyte.api.model.OAuth2Specification;
import io.airbyte.api.model.OAuthConfigSpecification;
import io.airbyte.commons.enums.Enums;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.List;
import java.util.Optional;

public class OauthModelConverter {

  public static Optional<AuthSpecification> getAuthSpec(final ConnectorSpecification spec) {
    if (spec.getAuthSpecification() == null) {
      return Optional.empty();
    }
    final io.airbyte.protocol.models.AuthSpecification incomingAuthSpec = spec.getAuthSpecification();

    final AuthSpecification authSpecification = new AuthSpecification();
    if (incomingAuthSpec.getAuthType() == io.airbyte.protocol.models.AuthSpecification.AuthType.OAUTH_2_0) {
      authSpecification.authType(AuthSpecification.AuthTypeEnum.OAUTH2_0)
          .oauth2Specification(new OAuth2Specification()
              .rootObject(incomingAuthSpec.getOauth2Specification().getRootObject())
              .oauthFlowInitParameters(incomingAuthSpec.getOauth2Specification().getOauthFlowInitParameters())
              .oauthFlowOutputParameters(incomingAuthSpec.getOauth2Specification().getOauthFlowOutputParameters()));
    }
    return Optional.of(authSpecification);
  }

  public static Optional<AdvancedAuth> getAdvancedAuth(final ConnectorSpecification spec) {
    if (spec.getAdvancedAuth() == null) {
      return Optional.empty();
    }
    final io.airbyte.protocol.models.AdvancedAuth incomingAdvancedAuth = spec.getAdvancedAuth();
    final AdvancedAuth advancedAuth = new AdvancedAuth();
    if (List.of(io.airbyte.protocol.models.AdvancedAuth.AuthFlowType.OAUTH_1_0, io.airbyte.protocol.models.AdvancedAuth.AuthFlowType.OAUTH_2_0)
        .contains(incomingAdvancedAuth.getAuthFlowType())) {
      final io.airbyte.protocol.models.OAuthConfigSpecification incomingOAuthConfigSpecification = incomingAdvancedAuth.getOauthConfigSpecification();
      advancedAuth
          .authFlowType(Enums.convertTo(incomingAdvancedAuth.getAuthFlowType(), AuthFlowTypeEnum.class))
          .predicateKey(incomingAdvancedAuth.getPredicateKey())
          .predicateValue(incomingAdvancedAuth.getPredicateValue())
          .oauthConfigSpecification(new OAuthConfigSpecification()
              .oauthUserInputFromConnectorConfigSpecification(incomingOAuthConfigSpecification.getOauthUserInputFromConnectorConfigSpecification())
              .completeOAuthOutputSpecification(incomingOAuthConfigSpecification.getCompleteOauthOutputSpecification())
              .completeOAuthServerInputSpecification(incomingOAuthConfigSpecification.getCompleteOauthServerInputSpecification())
              .completeOAuthServerOutputSpecification(incomingOAuthConfigSpecification.getCompleteOauthServerOutputSpecification()));
    }
    return Optional.of(advancedAuth);
  }

}

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import io.airbyte.api.model.generated.AdvancedAuth;
import io.airbyte.api.model.generated.AdvancedAuth.AuthFlowTypeEnum;
import io.airbyte.api.model.generated.AuthSpecification;
import io.airbyte.api.model.generated.OAuth2Specification;
import io.airbyte.api.model.generated.OAuthConfigSpecification;
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
      final AuthFlowTypeEnum oauthFlowType;
      if (io.airbyte.protocol.models.AdvancedAuth.AuthFlowType.OAUTH_1_0.equals(incomingAdvancedAuth.getAuthFlowType())) {
        oauthFlowType = AuthFlowTypeEnum.OAUTH1_0;
      } else {
        oauthFlowType = AuthFlowTypeEnum.OAUTH2_0;
      }
      final io.airbyte.protocol.models.OAuthConfigSpecification incomingOAuthConfigSpecification = incomingAdvancedAuth.getOauthConfigSpecification();
      advancedAuth
          .authFlowType(oauthFlowType)
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

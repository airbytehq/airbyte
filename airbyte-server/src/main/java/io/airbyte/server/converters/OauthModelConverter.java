/*
 * Copyright (c) 2020 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.AuthSpecification;
import io.airbyte.api.model.OAuth2Specification;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.Optional;

public class OauthModelConverter {

  public static Optional<AuthSpecification> getAuthSpec(ConnectorSpecification spec) {
    if (spec.getAuthSpecification() == null) {
      return Optional.empty();
    }
    io.airbyte.protocol.models.AuthSpecification incomingAuthSpec = spec.getAuthSpecification();

    AuthSpecification authSpecification = new AuthSpecification();
    if (incomingAuthSpec.getAuthType() == io.airbyte.protocol.models.AuthSpecification.AuthType.OAUTH_2_0) {
      authSpecification.authType(AuthSpecification.AuthTypeEnum.OAUTH2_0)
          .oauth2Specification(new OAuth2Specification()
              .oauthFlowInitParameters(incomingAuthSpec.getOauth2Specification().getOauthFlowInitParameters()));
    }

    return Optional.ofNullable(authSpecification);
  }

}

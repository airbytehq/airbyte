/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
              .rootObject(incomingAuthSpec.getOauth2Specification().getRootObject())
              .oauthFlowInitParameters(incomingAuthSpec.getOauth2Specification().getOauthFlowInitParameters())
              .oauthFlowOutputParameters(incomingAuthSpec.getOauth2Specification().getOauthFlowOutputParameters()));
    }

    return Optional.ofNullable(authSpecification);
  }

}

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

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.protocol.models.AuthSpecification;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.OAuth2Specification;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

class OauthModelConverterTest {

  private static Stream<Arguments> testProvider() {
    return Stream.of(
        // all fields filled out with nesting
        Arguments.of(
            List.of(List.of("init1"), List.of("init2-1", "init2-2")),
            List.of(List.of("output1"), List.of("output2-1", "output2-2")),
            List.of("path")),
        // init params only
        Arguments.of(
            List.of(List.of("init1"), List.of("init2-1", "init2-2")),
            List.of(List.of()),
            List.of()),
        // output params only
        Arguments.of(
            List.of(List.of()),
            List.of(List.of("output1"), List.of("output2-1", "output2-2")),
            List.of()),
        // rootObject only
        Arguments.of(
            List.of(List.of()),
            List.of(List.of()),
            List.of("path")));
  }

  @ParameterizedTest
  @MethodSource("testProvider")
  public void testIt(List<List<String>> initParams, List<List<String>> outputParams, List<String> rootObject) {
    ConnectorSpecification input = new ConnectorSpecification().withAuthSpecification(
        new AuthSpecification()
            .withAuthType(AuthSpecification.AuthType.OAUTH_2_0)
            .withOauth2Specification(new OAuth2Specification()
                .withOauthFlowInitParameters(initParams)
                .withOauthFlowOutputParameters(outputParams)
                .withRootObject(rootObject)));

    io.airbyte.api.model.AuthSpecification expected = new io.airbyte.api.model.AuthSpecification()
        .authType(io.airbyte.api.model.AuthSpecification.AuthTypeEnum.OAUTH2_0)
        .oauth2Specification(
            new io.airbyte.api.model.OAuth2Specification()
                .oauthFlowInitParameters(initParams)
                .oauthFlowOutputParameters(outputParams)
                .rootObject(rootObject));

    Optional<io.airbyte.api.model.AuthSpecification> authSpec = OauthModelConverter.getAuthSpec(input);
    assertTrue(authSpec.isPresent());
    assertEquals(expected, authSpec.get());
  }

}

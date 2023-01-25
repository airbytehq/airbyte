/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

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
            List.of("path", "nestedPath", 1)),
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
            List.of("path", "nestedPath", 1)));
  }

  @ParameterizedTest
  @MethodSource("testProvider")
  void testIt(final List<List<String>> initParams, final List<List<String>> outputParams, final List<Object> rootObject) {
    final ConnectorSpecification input = new ConnectorSpecification().withAuthSpecification(
        new AuthSpecification()
            .withAuthType(AuthSpecification.AuthType.OAUTH_2_0)
            .withOauth2Specification(new OAuth2Specification()
                .withOauthFlowInitParameters(initParams)
                .withOauthFlowOutputParameters(outputParams)
                .withRootObject(rootObject)));

    final io.airbyte.api.model.generated.AuthSpecification expected = new io.airbyte.api.model.generated.AuthSpecification()
        .authType(io.airbyte.api.model.generated.AuthSpecification.AuthTypeEnum.OAUTH2_0)
        .oauth2Specification(
            new io.airbyte.api.model.generated.OAuth2Specification()
                .oauthFlowInitParameters(initParams)
                .oauthFlowOutputParameters(outputParams)
                .rootObject(rootObject));

    final Optional<io.airbyte.api.model.generated.AuthSpecification> authSpec = OauthModelConverter.getAuthSpec(input);
    assertTrue(authSpec.isPresent());
    assertEquals(expected, authSpec.get());
  }

}

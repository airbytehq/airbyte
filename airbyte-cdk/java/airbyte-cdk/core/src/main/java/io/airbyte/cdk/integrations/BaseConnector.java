/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations;

import io.airbyte.cdk.integrations.base.Integration;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalUnit;
import java.util.Map;
import java.util.Optional;

public abstract class BaseConnector implements Integration {

  /**
   * By convention the spec is stored as a resource for java connectors. That resource is called
   * spec.json.
   *
   * @return specification.
   * @throws Exception - any exception.
   */
  @Override
  public ConnectorSpecification spec() throws Exception {
    // return a JsonSchema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  public static final String CONNECT_TIMEOUT_KEY = "connectTimeout";
  public static final Duration CONNECT_TIMEOUT_DEFAULT = Duration.ofSeconds(60);

  public static Optional<Duration> maybeParseDuration(final String stringValue, TemporalUnit unit) {
    if (stringValue == null) {
      return Optional.empty();
    }
    final long number;
    try {
      number = Long.parseLong(stringValue);
    } catch (NumberFormatException __) {
      return Optional.empty();
    }
    if (number < 0) {
      return Optional.empty();
    }
    return Optional.of(Duration.of(number, unit));
  }

}

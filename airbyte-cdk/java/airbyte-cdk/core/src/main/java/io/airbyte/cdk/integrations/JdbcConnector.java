package io.airbyte.cdk.integrations;

import java.time.Duration;
import java.time.temporal.TemporalUnit;
import java.util.Optional;

public abstract class JdbcConnector extends BaseConnector {
  public static final Duration CONNECT_TIMEOUT_DEFAULT = Duration.ofSeconds(60);
  public static final String CONNECT_TIMEOUT_KEY = "connectTimeout";

  protected final Optional<Duration> maybeParseDuration(final String stringValue, TemporalUnit unit) {
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

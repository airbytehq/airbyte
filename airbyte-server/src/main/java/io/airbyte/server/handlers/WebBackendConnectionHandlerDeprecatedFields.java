package io.airbyte.server.handlers;

import io.airbyte.config.persistence.ConfigRepository;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@AllArgsConstructor
public abstract class WebBackendConnectionHandlerDeprecatedFields {

  @Getter(value = AccessLevel.PROTECTED, onMethod = @__({@Deprecated(forRemoval = true)}))
  @Setter(value = AccessLevel.PROTECTED)
  final private ConfigRepository configRepository;
}

package io.airbyte.server.config;

import io.micronaut.context.annotation.Factory;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.util.UUID;
import java.util.function.Supplier;

@Factory
public class ApplicationBeanFactory {

  @Singleton
  @Named("randomUUIDSupplier")
  public Supplier<UUID> randomUUIDSupplier() {
    return () -> UUID.randomUUID();
  }

}

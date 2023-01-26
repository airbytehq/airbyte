/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader.config;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.init.LocalDefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Optional;

/**
 * Micronaut bean factory for general application-related singletons.
 */
@Factory
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class ApplicationBeanFactory {

  @Singleton
  public AirbyteVersion airbyteVersion(@Value("${airbyte.version}") final String version) {
    return new AirbyteVersion(version);
  }

  @Singleton
  public AirbyteProtocolVersionRange airbyteProtocolTargetVersionRange(@Value("${airbyte.protocol.target.range.min-version}") final String min,
                                                                       @Value("${airbyte.protocol.target.range.max-version}") final String max) {
    return new AirbyteProtocolVersionRange(new Version(min), new Version(max));
  }

  @Singleton
  public DefinitionsProvider localDefinitionsProvider() throws IOException {
    return new LocalDefinitionsProvider(LocalDefinitionsProvider.DEFAULT_SEED_DEFINITION_RESOURCE_CLASS);
  }

  @Singleton
  public FeatureFlags featureFlags() {
    return new EnvVariableFeatureFlags();
  }

  @Singleton
  public JsonSecretsProcessor jsonSecretsProcessor() {
    return JsonSecretsProcessor.builder()
        .copySecrets(false)
        .build();
  }

  @Singleton
  public SecretsRepositoryReader secretsRepositoryReader(final ConfigRepository configRepository, final SecretsHydrator secretsHydrator) {
    return new SecretsRepositoryReader(configRepository, secretsHydrator);
  }

  @Singleton
  public SecretsRepositoryWriter secretsRepositoryWriter(final ConfigRepository configRepository,
                                                         @Named("secretPersistence") final Optional<SecretPersistence> secretPersistence,
                                                         @Named("ephemeralSecretPersistence") final Optional<SecretPersistence> ephemeralSecretPersistence) {
    return new SecretsRepositoryWriter(configRepository, secretPersistence, ephemeralSecretPersistence);
  }

}

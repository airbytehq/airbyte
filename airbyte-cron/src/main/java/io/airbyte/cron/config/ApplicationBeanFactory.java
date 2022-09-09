/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.config;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.micronaut.context.annotation.Factory;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for general singletons.
 */
@Factory
@Slf4j
public class ApplicationBeanFactory {

  @Singleton
  public FeatureFlags featureFlags() {
    return new EnvVariableFeatureFlags();
  }

  @Singleton
  public JsonSecretsProcessor jsonSecretsProcessor(final FeatureFlags featureFlags) {
    return JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
  }

}

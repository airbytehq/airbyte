/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.config;

import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for general singletons.
 */
@Factory
@Slf4j
public class ApplicationBeanFactory {

  @Singleton
  public JsonSecretsProcessor jsonSecretsProcessor() {
    return JsonSecretsProcessor.builder()
        .copySecrets(false)
        .build();
  }

}

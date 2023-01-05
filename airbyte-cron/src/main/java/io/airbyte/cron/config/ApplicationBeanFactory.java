/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.config;

import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import io.micronaut.core.util.StringUtils;
import jakarta.inject.Singleton;
import java.util.Locale;
import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for general singletons.
 */
@Factory
@Slf4j
public class ApplicationBeanFactory {

  @Singleton
  public DeploymentMode deploymentMode(@Value("${airbyte.deployment-mode}") final String deploymentMode) {
    return convertToEnum(deploymentMode, DeploymentMode::valueOf, DeploymentMode.OSS);
  }

  @Singleton
  public JsonSecretsProcessor jsonSecretsProcessor() {
    return JsonSecretsProcessor.builder()
        .copySecrets(false)
        .build();
  }

  private <T> T convertToEnum(final String value, final Function<String, T> creatorFunction, final T defaultValue) {
    return StringUtils.isNotEmpty(value) ? creatorFunction.apply(value.toUpperCase(Locale.ROOT)) : defaultValue;
  }

}

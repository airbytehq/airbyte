/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.config;

import io.micronaut.context.annotation.Factory;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for general singletons.
 */
@Factory
@Slf4j
public class FeatureFlagFactory {

  // private static final String CONFIG_LD_KEY = "airbyte.feature-flag.api-key";
  // private static final String CONFIG_OSS_KEY = "airbyte.feature-flag.path";

  // @Requires(property = CONFIG_LD_KEY,
  // defaultValue = DEFAULT_MISSING,
  // notEquals = DEFAULT_MISSING)
  // @Singleton
  // FeatureFlagClient LaunchDarklyClient(@Property(name = CONFIG_LD_KEY) final String apiKey) {
  // log.info("!!! starting ld client !!!");
  // final var client = new LDClient(apiKey);
  // return new LaunchDarklyClient(client);
  // }

  // @Singleton
  // FeatureFlagClient featureFlagClient(
  // @Property(name = CONFIG_LD_KEY) final String apiKey,
  // @Property(name = CONFIG_OSS_KEY) final String configPath) {
  // log.info("!!! values {} {} !!!", apiKey, configPath);
  // if (apiKey != null && !apiKey.equals("")) {
  // log.info("!!! starting ld client !!!");
  // final var client = new LDClient(apiKey);
  // return new LaunchDarklyClient(client);
  // }
  //
  // log.info("!!! starting config client2 !!!");
  // final Path path;
  // if (configPath == null || configPath.equals("")) {
  // path = null;
  // } else {
  // path = Path.of(configPath);
  // }
  //
  // return new ConfigFileClient(path);
  // }

  // @Requires(property = CONFIG_LD_KEY,
  // value = "")
  // @Singleton
  // FeatureFlagClient ConfigFileClient(@Property(name = CONFIG_OSS_KEY) final String configPath) {
  // log.info("!!! starting config client !!!");
  // final Path path;
  // if (configPath == null || configPath.equals("")) {
  // path = null;
  // } else {
  // path = Path.of(configPath);
  // }
  //
  // return new ConfigFileClient(path);
  // }

  // @Requires(missingProperty = CONFIG_LD_KEY)
  // @Requires(property = CONFIG_LD_KEY,
  // defaultValue = DEFAULT_MISSING,
  // value = DEFAULT_MISSING)
  // @Singleton
  // FeatureFlagClient ConfigFileClient2(@Property(name = CONFIG_OSS_KEY) final String configPath) {
  // log.info("!!! starting config client2 !!!");
  // final Path path;
  // if (configPath == null || configPath.equals("")) {
  // path = null;
  // } else {
  // path = Path.of(configPath);
  // }
  //
  // return new ConfigFileClient(path);
  // }

}

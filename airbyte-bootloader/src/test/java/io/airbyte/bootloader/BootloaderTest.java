/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.context.event.StartupEvent;
import io.micronaut.core.util.StringUtils;
import io.micronaut.test.annotation.MockBean;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import javax.inject.Inject;
import javax.inject.Named;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;

@MicronautTest
@Requires(env = {Environment.TEST})
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.FALSE,
          value = StringUtils.TRUE)
public class BootloaderTest {

  @Inject
  private Bootloader bootloader;

  @Inject
  @Named("configFlyway")
  private Flyway configFlyway;

  @Inject
  @Named("jobsFlyway")
  private Flyway jobsFlyway;

  @Inject
  private FeatureFlags featureFlags;

  @Inject
  private ConfigPersistence configPersistence;

  @MockBean(AirbyteVersion.class)
  AirbyteVersion airbyteVersion() {
    return new AirbyteVersion("0.33.0-alpha");
  }

  @MockBean(Flyway.class)
  @Named("configFlyway")
  Flyway configFlyway() {
    return mock(Flyway.class);
  }

  @MockBean(Flyway.class)
  @Named("jobsFlyway")
  Flyway jobsFlyway() {
    return mock(Flyway.class);
  }

  @MockBean(FeatureFlags.class)
  FeatureFlags featureFlags() {
    return mock(FeatureFlags.class);
  }

  @MockBean(ConfigPersistence.class)
  ConfigPersistence configPersistence() {
    return mock(ConfigPersistence.class);
  }

  @MockBean(ConfigRepository.class)
  ConfigRepository configRepository() {
    return mock(ConfigRepository.class);
  }

  @Test
  void testBootloaderAppBlankDb() throws Exception {
    when(featureFlags.usesNewScheduler()).thenReturn(false);

    bootloader.onStartup(mock(StartupEvent.class));

    verify(configFlyway, times(1)).baseline();
    verify(configFlyway, times(1)).migrate();
    verify(jobsFlyway, times(1)).baseline();
    verify(jobsFlyway, times(1)).migrate();
  }

  @Test
  void testIsLegalUpgradePredicate() {
    // starting from no previous version is always legal.
    assertTrue(Bootloader.isLegalUpgrade(null, new AirbyteVersion("0.17.1-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(null, new AirbyteVersion("0.32.0-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(null, new AirbyteVersion("0.32.1-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(null, new AirbyteVersion("0.33.1-alpha")));
    // starting from a version that is pre-breaking migration cannot go past the breaking migration.
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.17.1-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.18.0-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.32.0-alpha")));
    assertFalse(Bootloader.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertFalse(Bootloader.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.33.0-alpha")));
    // any migration starting at the breaking migration or after it can upgrade to anything.
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.32.0-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.32.0-alpha"), new AirbyteVersion("0.33.0-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.32.1-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.32.1-alpha"), new AirbyteVersion("0.33.0-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.33.0-alpha"), new AirbyteVersion("0.33.1-alpha")));
    assertTrue(Bootloader.isLegalUpgrade(new AirbyteVersion("0.33.0-alpha"), new AirbyteVersion("0.34.0-alpha")));
  }

  @Test
  void testPostLoadExecutionExecutes() throws Exception {
    bootloader.afterInitialization();
    bootloader.onStartup(mock(StartupEvent.class));
    verify(configPersistence, times(1)).loadData(any(YamlSeedConfigPersistence.class));
  }

}

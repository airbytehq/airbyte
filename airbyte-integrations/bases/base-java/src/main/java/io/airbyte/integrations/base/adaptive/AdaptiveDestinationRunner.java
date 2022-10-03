/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.adaptive;

import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class launches different variants of a destination connector based on where Airbyte is
 * deployed.
 */
public class AdaptiveDestinationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(AdaptiveDestinationRunner.class);

  private static final String DEPLOYMENT_MODE_KEY = "DEPLOYMENT_MODE";
  private static final String CLOUD_MODE = "CLOUD";

  public static OssDestinationBuilder baseOnEnv() {
    final String mode = System.getenv(DEPLOYMENT_MODE_KEY);
    return new OssDestinationBuilder(mode);
  }

  public static final class OssDestinationBuilder {

    private final String deploymentMode;

    private OssDestinationBuilder(final String deploymentMode) {
      this.deploymentMode = deploymentMode;
    }

    public <OT extends Destination> CloudDestinationBuilder<OT> withOssDestination(final Supplier<OT> ossDestinationSupplier) {
      return new CloudDestinationBuilder<>(deploymentMode, ossDestinationSupplier);
    }

  }

  public static final class CloudDestinationBuilder<OT extends Destination> {

    private final String deploymentMode;
    private final Supplier<OT> ossDestinationSupplier;

    public CloudDestinationBuilder(final String deploymentMode, final Supplier<OT> ossDestinationSupplier) {
      this.deploymentMode = deploymentMode;
      this.ossDestinationSupplier = ossDestinationSupplier;
    }

    public <CT extends Destination> Runner<OT, CT> withCloudDestination(final Supplier<CT> cloudDestinationSupplier) {
      return new Runner<>(deploymentMode, ossDestinationSupplier, cloudDestinationSupplier);
    }

  }

  public static final class Runner<OT extends Destination, CT extends Destination> {

    private final String deploymentMode;
    private final Supplier<OT> ossDestinationSupplier;
    private final Supplier<CT> cloudDestinationSupplier;

    public Runner(final String deploymentMode,
                  final Supplier<OT> ossDestinationSupplier,
                  final Supplier<CT> cloudDestinationSupplier) {
      this.deploymentMode = deploymentMode;
      this.ossDestinationSupplier = ossDestinationSupplier;
      this.cloudDestinationSupplier = cloudDestinationSupplier;
    }

    private Destination getDestination() {
      LOGGER.info("Running destination under deployment mode: {}", deploymentMode);
      if (deploymentMode != null && deploymentMode.equals(CLOUD_MODE)) {
        return cloudDestinationSupplier.get();
      }
      if (deploymentMode == null) {
        LOGGER.warn("Deployment mode is null, default to OSS mode");
      }
      return ossDestinationSupplier.get();
    }

    public void run(final String[] args) throws Exception {
      final Destination destination = getDestination();
      LOGGER.info("Starting destination: {}", destination.getClass().getName());
      new IntegrationRunner(destination).run(args);
      LOGGER.info("Completed destination: {}", destination.getClass().getName());
    }

  }

}

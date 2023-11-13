/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base.adaptive;

import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class launches different variants of a source connector based on where Airbyte is deployed.
 */
public class AdaptiveSourceRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(AdaptiveSourceRunner.class);

  public static final String DEPLOYMENT_MODE_KEY = EnvVariableFeatureFlags.DEPLOYMENT_MODE;
  public static final String CLOUD_MODE = "CLOUD";

  public static OssSourceBuilder baseOnEnv() {
    final String mode = System.getenv(DEPLOYMENT_MODE_KEY);
    return new OssSourceBuilder(mode);
  }

  public static final class OssSourceBuilder {

    private final String deploymentMode;

    private OssSourceBuilder(final String deploymentMode) {
      this.deploymentMode = deploymentMode;
    }

    public <OT extends Source> CloudSourceBuilder<OT> withOssSource(final Supplier<OT> ossSourceSupplier) {
      return new CloudSourceBuilder<>(deploymentMode, ossSourceSupplier);
    }

  }

  public static final class CloudSourceBuilder<OT extends Source> {

    private final String deploymentMode;
    private final Supplier<OT> ossSourceSupplier;

    public CloudSourceBuilder(final String deploymentMode, final Supplier<OT> ossSourceSupplier) {
      this.deploymentMode = deploymentMode;
      this.ossSourceSupplier = ossSourceSupplier;
    }

    public <CT extends Source> Runner<OT, CT> withCloudSource(final Supplier<CT> cloudSourceSupplier) {
      return new Runner<>(deploymentMode, ossSourceSupplier, cloudSourceSupplier);
    }

  }

  public static final class Runner<OT extends Source, CT extends Source> {

    private final String deploymentMode;
    private final Supplier<OT> ossSourceSupplier;
    private final Supplier<CT> cloudSourceSupplier;

    public Runner(final String deploymentMode,
                  final Supplier<OT> ossSourceSupplier,
                  final Supplier<CT> cloudSourceSupplier) {
      this.deploymentMode = deploymentMode;
      this.ossSourceSupplier = ossSourceSupplier;
      this.cloudSourceSupplier = cloudSourceSupplier;
    }

    private Source getSource() {
      LOGGER.info("Running source under deployment mode: {}", deploymentMode);
      if (deploymentMode != null && deploymentMode.equals(CLOUD_MODE)) {
        return cloudSourceSupplier.get();
      }
      if (deploymentMode == null) {
        LOGGER.warn("Deployment mode is null, default to OSS mode");
      }
      return ossSourceSupplier.get();
    }

    public void run(final String[] args) throws Exception {
      final Source source = getSource();
      LOGGER.info("Starting source: {}", source.getClass().getName());
      new IntegrationRunner(source).run(args);
      LOGGER.info("Completed source: {}", source.getClass().getName());
    }

  }

}

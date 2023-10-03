package io.airbyte.cdk.integrations.standardtest.destination;

public class TestEnvConfigs {

  public static final String DEPLOYMENT_MODE = "DEPLOYMENT_MODE";

  public enum DeploymentMode {
    OSS,
    CLOUD
  }

}

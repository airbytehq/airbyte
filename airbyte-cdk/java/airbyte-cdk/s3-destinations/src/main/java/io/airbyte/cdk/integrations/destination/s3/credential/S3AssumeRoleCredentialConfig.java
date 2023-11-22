/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.credential;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicSessionCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClient;
import com.amazonaws.services.securitytoken.model.AssumeRoleRequest;

public class S3AssumeRoleCredentialConfig implements S3CredentialConfig {

  private String roleArn;
  private String externalId;

  public S3AssumeRoleCredentialConfig(final String roleArn) {
    this.roleArn = roleArn;
    this.externalId = System.getenv("AWS_EXTERNAL_ID");
  }

  @Override
  public S3CredentialType getCredentialType() {
    return S3CredentialType.ASSUME_ROLE;
  }

  @Override
  public AWSCredentialsProvider getS3CredentialsProvider() {
    final var stsClient = AWSSecurityTokenServiceClient
        .builder()
        .withRegion(Regions.DEFAULT_REGION)
        .build();

    // Call the assumeRole method of the STSRegionalEndpointClient object.
    var assumeRoleRequest = new AssumeRoleRequest();
    assumeRoleRequest.setRoleArn(roleArn);
    if (externalId != null) {
      assumeRoleRequest.setExternalId(externalId);
    }
    assumeRoleRequest.setRoleSessionName("airbyte");
    var assumeRoleResponse = stsClient.assumeRole(assumeRoleRequest);
    final var credentials = assumeRoleResponse.getCredentials();
    return new AWSStaticCredentialsProvider(
        new BasicSessionCredentials(
            credentials.getAccessKeyId(),
            credentials.getSecretAccessKey(),
            credentials.getSessionToken()));
  }

}

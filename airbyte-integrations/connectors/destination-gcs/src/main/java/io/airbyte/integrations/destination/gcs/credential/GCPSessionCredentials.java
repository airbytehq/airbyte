package io.airbyte.integrations.destination.gcs.credential;

import com.amazonaws.auth.AWSSessionCredentials;
import com.google.auth.oauth2.GoogleCredentials;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.credential.S3CredentialConfig;
import java.io.IOException;
import java.util.Optional;

public class GCPSessionCredentials implements AWSSessionCredentials, GcsCredentialConfig {
  private final GoogleCredentials credentials;

  @Override
  public Optional<S3CredentialConfig> getS3CredentialConfig() {
    return Optional.of(new S3AccessKeyCredentialConfig(getAWSAccessKeyId(), getAWSSecretKey()));
  }

  @Override
  public GcsCredentialType getCredentialType() {
    return GcsCredentialType.OAUTH2;
  }

  public GCPSessionCredentials(GoogleCredentials credentials) {
    this.credentials = credentials;
  }

  private String getGCPToken() {
    try {
      this.credentials.refreshIfExpired();
    } catch (IOException ioex) {
      return "";
    }
    return credentials.getAccessToken().getTokenValue();
  }

  public String getAWSAccessKeyId() {
    return getGCPToken();
  }

  public String getAWSSecretKey() {
    return "";
  }

  public String getSessionToken() {
    return "";
  }
}

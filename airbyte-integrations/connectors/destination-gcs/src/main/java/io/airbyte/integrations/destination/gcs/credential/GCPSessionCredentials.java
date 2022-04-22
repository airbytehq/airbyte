package io.airbyte.integrations.destination.gcs.credential;

import com.amazonaws.auth.AWSSessionCredentials;
import com.google.auth.oauth2.GoogleCredentials;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.credential.S3CredentialConfig;
import java.io.IOException;
import java.util.Optional;

public record GCPSessionCredentials(GoogleCredentials credentials) implements AWSSessionCredentials, GcsCredentialConfig {

  @Override
  public Optional<S3CredentialConfig> getS3CredentialConfig() {
    return Optional.of(new S3AccessKeyCredentialConfig(getAWSAccessKeyId(), getAWSSecretKey()));
  }

  @Override
  public GcsCredentialType getCredentialType() {
    return GcsCredentialType.OAUTH2;
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

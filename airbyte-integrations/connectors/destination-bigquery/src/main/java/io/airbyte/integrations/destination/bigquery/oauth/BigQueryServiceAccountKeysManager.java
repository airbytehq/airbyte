package io.airbyte.integrations.destination.bigquery.oauth;

import static com.google.api.client.json.jackson2.JacksonFactory.*;

import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.services.iam.v1.Iam;
import com.google.api.services.iam.v1.IamScopes;
import com.google.api.services.iam.v1.model.CreateServiceAccountKeyRequest;
import com.google.api.services.iam.v1.model.ServiceAccountKey;
import com.google.auth.http.HttpCredentialsAdapter;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.Collections;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryServiceAccountKeysManager {
  // Creates a key for a service account. See

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryServiceAccountKeysManager.class);

  public static ServiceAccountKey createKey(String projectId, String serviceAccountName, String tokenValue) {
    Iam service;
    try {
      service = initService(tokenValue);
    } catch (IOException | GeneralSecurityException e) {
      LOGGER.error("Unable to initialize service: {}", e.toString());
      return null;
    }

    String serviceAccountEmail = getServiceAccountEmail(serviceAccountName, projectId);
    try {
      ServiceAccountKey key =
          service
              .projects()
              .serviceAccounts()
              .keys()
              .create(
                  "projects/-/serviceAccounts/" + serviceAccountEmail,
                  new CreateServiceAccountKeyRequest())

              .execute();
      LOGGER.info("Created key: {}", key.getName());
      return key;
    } catch (IOException e) {
      LOGGER.error("Unable to create service account key: {}", e.getMessage());
    }
    return null;
  }

  // Lists all keys for a service account.
  public static void listKeys(String projectId, String serviceAccountName, String tokenValue) {
    Iam service;
    try {
      service = initService(tokenValue);
    } catch (IOException | GeneralSecurityException e) {
      LOGGER.error("Unable to initialize service: {}", e.getMessage());
      return;
    }

    String serviceAccountEmail = getServiceAccountEmail(serviceAccountName, projectId);
    try {
      List<ServiceAccountKey> keys =
          service
              .projects()
              .serviceAccounts()
              .keys()
              .list("projects/-/serviceAccounts/" + serviceAccountEmail)
              .execute()
              .getKeys();

      keys.forEach(key -> LOGGER.info("Key: {}", key));

    } catch (IOException e) {
      LOGGER.error("Unable to list service account keys: {}", e.getMessage());
    }
  }

  private static String getServiceAccountEmail(String serviceAccountName, String projectId) {
    return serviceAccountName + "@" + projectId + ".iam.gserviceaccount.com";
  }

  private static Iam initService(String tokenValue) throws GeneralSecurityException, IOException {
    // Use the Application Default Credentials strategy for authentication. For more info, see:
    // https://cloud.google.com/docs/authentication/production#finding_credentials_automatically
    AccessToken accessToken = new AccessToken(tokenValue, null);
    GoogleCredentials credential =
        GoogleCredentials.create(accessToken).createScoped(Collections.singleton(IamScopes.CLOUD_PLATFORM));
    // Initialize the IAM service, which can be used to send requests to the IAM API.
    return new Iam.Builder(
            GoogleNetHttpTransport.newTrustedTransport(),
            getDefaultInstance(),
            new HttpCredentialsAdapter(credential))
            .setApplicationName("service-account-keys")
            .build();
  }
}

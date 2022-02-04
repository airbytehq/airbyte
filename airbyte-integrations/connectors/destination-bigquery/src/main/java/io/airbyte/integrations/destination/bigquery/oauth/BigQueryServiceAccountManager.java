package io.airbyte.integrations.destination.bigquery.oauth;

import static com.google.api.client.json.jackson2.JacksonFactory.*;

import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.services.iam.v1.Iam;
import com.google.api.services.iam.v1.IamScopes;
import com.google.api.services.iam.v1.model.CreateServiceAccountRequest;
import com.google.api.services.iam.v1.model.ServiceAccount;
import com.google.auth.http.HttpCredentialsAdapter;
import com.google.auth.oauth2.GoogleCredentials;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.Collections;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryServiceAccountManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryServiceAccountManager.class);

  // Creates a service account.
  public static void createServiceAccount(String projectId, String serviceAccountName) {

    Iam service;
    try {
      service = initService();
    } catch (IOException | GeneralSecurityException e) {
      LOGGER.error("Unable to initialize service: {}", e.getMessage());
      return;
    }

    try {
      ServiceAccount serviceAccount = new ServiceAccount();
      serviceAccount.setDisplayName("bigquery-service-account");
      CreateServiceAccountRequest request = new CreateServiceAccountRequest();
      request.setAccountId(serviceAccountName);
      request.setServiceAccount(serviceAccount);

      serviceAccount =
          service.projects().serviceAccounts().create("projects/" + projectId, request).execute();

      LOGGER.info("Created service account: {}", serviceAccount.getEmail());
    } catch (IOException e) {
      LOGGER.error("Unable to create service account: {}", e.toString());
    }
  }

  private static Iam initService() throws GeneralSecurityException, IOException {
    // Use the Application Default Credentials strategy for authentication. For more info, see:
    // https://cloud.google.com/docs/authentication/production#finding_credentials_automatically
    GoogleCredentials credential =
        GoogleCredentials.getApplicationDefault()
            .createScoped(Collections.singleton(IamScopes.CLOUD_PLATFORM));
    // Initialize the IAM service, which can be used to send requests to the IAM API.
    return new Iam.Builder(
        GoogleNetHttpTransport.newTrustedTransport(),
        getDefaultInstance(),
        new HttpCredentialsAdapter(credential))
        .setApplicationName("service-accounts")
        .build();
  }
}
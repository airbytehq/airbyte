package io.airbyte.integrations.destination.bigquery.oauth;

import static com.google.api.client.json.jackson2.JacksonFactory.*;

import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.services.iam.v1.Iam;
import com.google.api.services.iam.v1.IamScopes;
import com.google.api.services.iam.v1.model.Binding;
import com.google.api.services.iam.v1.model.CreateServiceAccountRequest;
import com.google.api.services.iam.v1.model.Policy;
import com.google.api.services.iam.v1.model.ServiceAccount;
import com.google.api.services.iam.v1.model.SetIamPolicyRequest;
import com.google.auth.http.HttpCredentialsAdapter;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryServiceAccountManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryServiceAccountManager.class);

  // Creates a service account.
  public static ServiceAccount createServiceAccount(String projectId, String serviceAccountName, String accessToken, Date date) {
    ServiceAccount result = null;
    boolean finished = false;

    Iam service = null;
    try {
      service = initService(accessToken, date);
    } catch (IOException | GeneralSecurityException e) {
      LOGGER.error("Unable to initialize service: {}", e.getMessage());
      finished = true;
    }
    if (!finished) {
      try {
        ServiceAccount serviceAccount = new ServiceAccount();

        serviceAccount.setDisplayName("bigquery-service-account");
        CreateServiceAccountRequest request = new CreateServiceAccountRequest();
        request.setAccountId(serviceAccountName);
        request.setServiceAccount(serviceAccount);
        serviceAccount =
            service.projects()
                .serviceAccounts()
                .create("projects/" + projectId, request).execute();
        LOGGER.info("Created service account: {}", serviceAccount.getEmail());
        result = serviceAccount;
        SetIamPolicyRequest requestBody = new SetIamPolicyRequest();
        Policy policy = new Policy();
        Binding binding = new Binding();
        binding.setMembers(List.of("serviceAccount:" + serviceAccount.getEmail()));
        binding.setRole("roles/editor");
        policy.setBindings(List.of(binding));
        requestBody.setPolicy(policy);
        service.projects().serviceAccounts().setIamPolicy("projects/"+ projectId + "/serviceAccounts/"+serviceAccount.getEmail(), requestBody).execute();

      } catch (IOException e) {
        LOGGER.error("Unable to create service account: {}", e.toString());
      }
    }

    return result;
  }

  private static Iam initService(String tokenValue, Date date) throws GeneralSecurityException, IOException {
    AccessToken accessToken = new AccessToken(tokenValue, null);
    GoogleCredentials credential =
        GoogleCredentials.create(accessToken).createScoped();
    // Initialize the IAM service, which can be used to send requests to the IAM API.
    return new Iam.Builder(
        GoogleNetHttpTransport.newTrustedTransport(),
        getDefaultInstance(),
        new HttpCredentialsAdapter(credential))
        .setApplicationName("service-accounts")
        .build();
  }
}
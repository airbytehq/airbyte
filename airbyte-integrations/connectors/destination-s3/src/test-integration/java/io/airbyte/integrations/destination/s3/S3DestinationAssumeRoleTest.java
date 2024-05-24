/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.amazonaws.regions.Regions;
import com.amazonaws.services.identitymanagement.AmazonIdentityManagement;
import com.amazonaws.services.identitymanagement.AmazonIdentityManagementClientBuilder;
import com.amazonaws.services.identitymanagement.model.AttachRolePolicyRequest;
import com.amazonaws.services.identitymanagement.model.AttachedPolicy;
import com.amazonaws.services.identitymanagement.model.CreatePolicyRequest;
import com.amazonaws.services.identitymanagement.model.DeletePolicyRequest;
import com.amazonaws.services.identitymanagement.model.DetachRolePolicyRequest;
import com.amazonaws.services.identitymanagement.model.ListAttachedRolePoliciesRequest;
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory;
import io.airbyte.cdk.integrations.destination.s3.credential.S3AssumeRoleCredentialConfig;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

// Even though this looks like a unit test, it needs to be an integration test
// because it uses secrets, which are not available when running unit tests
// Plus, it does connect to S3, which makes it an integration test anyways
public class S3DestinationAssumeRoleTest {

  @Test
  void testFailsWithNoEnvCredentials() {
    S3Destination dest = new S3Destination(new S3DestinationConfigFactory(), Collections.emptyMap());
    assertEquals(Status.FAILED, dest.check(S3DestinationTestUtils.getAssumeRoleConfig()).getStatus());
  }

  @Test
  void testPassesWithAllCredentials() {
    S3Destination dest = new S3Destination(new S3DestinationConfigFactory(), S3DestinationTestUtils.getAssumeRoleInternalCredentials());
    assertEquals(Status.SUCCEEDED, dest.check(S3DestinationTestUtils.getAssumeRoleConfig()).getStatus());
  }

  @Test
  void testFailsWithWrongExternalId() {
    Map<String, String> envWithBadExternalId = new HashMap<>(S3DestinationTestUtils.getAssumeRoleInternalCredentials());
    envWithBadExternalId.put("AWS_ASSUME_ROLE_EXTERNAL_ID", "dummyValue");
    S3Destination dest = new S3Destination(new S3DestinationConfigFactory(), envWithBadExternalId);
    assertEquals(Status.FAILED, dest.check(S3DestinationTestUtils.getAssumeRoleConfig()).getStatus());
  }

  private static final String REVOKE_OLD_TOKENS_POLICY = """
                                                         {
                                                           "Version": "2012-10-17",
                                                           "Statement": {
                                                             "Effect": "Deny",
                                                             "Action": "*",
                                                             "Resource": [
                                                                 "arn:aws:s3:::airbyte-integration-test-destination-s3/*",
                                                                 "arn:aws:s3:::airbyte-integration-test-destination-s3"
                                                             ],
                                                             "Condition": {
                                                               "DateLessThan": {"aws:TokenIssueTime": "%s"}
                                                             }
                                                           }
                                                         }
                                                         """;
  private static final String POLICY_NAME_PREFIX = S3DestinationAssumeRoleTest.class.getSimpleName() + "Policy-";
  private static final String ASSUMED_ROLE_NAME = "s3_acceptance_test_iam_assume_role_role";

  // This test is a bit hairy. We assume a role, and then create a policy that denies ALL for any
  // token that were created before now().
  // This effectively cancels the token created above.
  // Then we double check that the deny policy is applied, and then explicitely call refresh, to make
  // sure
  // the token gets renewed. In a real prod case, the refresh is called by a background thread
  @Test
  @Timeout(value = 1,
           unit = TimeUnit.HOURS)
  void testAutomaticRenewal() throws InterruptedException {
    final AmazonIdentityManagement iam =
        AmazonIdentityManagementClientBuilder.standard().withRegion(Regions.DEFAULT_REGION)
            .withCredentials(S3AssumeRoleCredentialConfig.getCredentialProvider(S3DestinationTestUtils.getPolicyManagerCredentials())).build();
    ListAttachedRolePoliciesRequest listPoliciesRequest = new ListAttachedRolePoliciesRequest().withRoleName(ASSUMED_ROLE_NAME);
    List<AttachedPolicy> policies = iam.listAttachedRolePolicies(listPoliciesRequest).getAttachedPolicies();
    // We start deleting old deny policies that this test instance might have created. Just making sure
    // our S3 policies are reasonable
    for (AttachedPolicy policy : policies) {
      String policyName = policy.getPolicyName();
      if (policyName.startsWith(POLICY_NAME_PREFIX)) {
        String policyCreationDateString = policyName.substring(POLICY_NAME_PREFIX.length()).replace('_', ':');
        if (Instant.parse(policyCreationDateString).isBefore(Instant.now().minus(1, ChronoUnit.DAYS))) {
          DetachRolePolicyRequest detachPolicyRequest =
              new DetachRolePolicyRequest().withPolicyArn(policy.getPolicyArn()).withRoleName(ASSUMED_ROLE_NAME);
          iam.detachRolePolicy(detachPolicyRequest);
          DeletePolicyRequest deleteRequest = new DeletePolicyRequest().withPolicyArn(policy.getPolicyArn());
          iam.deletePolicy(deleteRequest);
        }
      }
    }

    Map<String, String> environmentForAssumeRole = S3DestinationTestUtils.getAssumeRoleInternalCredentials();
    S3DestinationConfig config = S3DestinationConfig.getS3DestinationConfig(S3DestinationTestUtils.getAssumeRoleConfig(), environmentForAssumeRole);
    var s3Client = config.getS3Client();
    S3BaseChecks.testSingleUpload(
        s3Client,
        config.getBucketName(),
        config.getBucketPath());

    // We wait 1 second so that the less than is strictly greater than the token generation time
    Thread.sleep(1000);
    String now = Instant.now().truncatedTo(ChronoUnit.SECONDS).toString();
    String policyName = POLICY_NAME_PREFIX + now.toString().replace(':', '_');

    String policyDocument = REVOKE_OLD_TOKENS_POLICY.formatted(now);
    CreatePolicyRequest createPolicyRequest = new CreatePolicyRequest()
        .withPolicyName(policyName)
        .withPolicyDocument(policyDocument);
    String arn = iam.createPolicy(createPolicyRequest).getPolicy().getArn();
    try {
      AttachRolePolicyRequest attachPolicyRequest =
          new AttachRolePolicyRequest()
              .withRoleName(ASSUMED_ROLE_NAME)
              .withPolicyArn(arn);

      iam.attachRolePolicy(attachPolicyRequest);
      // Experience showed than under 30sec, the policy is not applied. Giving it some buffer
      Thread.sleep(60_000);

      // We check that the deny policy is enforced
      assertThrows(Exception.class, () -> S3BaseChecks.testSingleUpload(
          s3Client,
          config.getBucketName(),
          config.getBucketPath()));
      // and force-refresh the token
      config.getS3CredentialConfig().getS3CredentialsProvider().refresh();
      S3BaseChecks.testSingleUpload(
          s3Client,
          config.getBucketName(),
          config.getBucketPath());
    } finally {
      DetachRolePolicyRequest detachPolicyRequest = new DetachRolePolicyRequest().withPolicyArn(arn).withRoleName(ASSUMED_ROLE_NAME);
      iam.detachRolePolicy(detachPolicyRequest);
      DeletePolicyRequest deleteRequest = new DeletePolicyRequest().withPolicyArn(arn);
      iam.deletePolicy(deleteRequest);
    }
  }

}

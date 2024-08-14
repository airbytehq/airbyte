/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.amazonaws.regions.Regions
import com.amazonaws.services.identitymanagement.AmazonIdentityManagementClientBuilder
import com.amazonaws.services.identitymanagement.model.*
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.testSingleUpload
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory
import io.airbyte.cdk.integrations.destination.s3.credential.S3AssumeRoleCredentialConfig
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

// Even though this looks like a unit test, it needs to be an integration test
// because it uses secrets, which are not available when running unit tests
// Plus, it does connect to S3, which makes it an integration test anyways
class S3DestinationAssumeRoleTest {
    @Test
    fun testFailsWithNoEnvCredentials() {
        val dest = S3Destination(S3DestinationConfigFactory(), emptyMap<String, String>())
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.FAILED,
            dest.check(S3DestinationTestUtils.assumeRoleConfig)!!.status
        )
    }

    @Test
    fun testPassesWithAllCredentials() {
        val dest =
            S3Destination(
                S3DestinationConfigFactory(),
                S3DestinationTestUtils.assumeRoleInternalCredentials
            )
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.SUCCEEDED,
            dest.check(S3DestinationTestUtils.assumeRoleConfig)!!.status
        )
    }

    @Test
    fun testFailsWithWrongExternalId() {
        val envWithBadExternalId: MutableMap<String, String> =
            HashMap(S3DestinationTestUtils.assumeRoleInternalCredentials)
        envWithBadExternalId["AWS_ASSUME_ROLE_EXTERNAL_ID"] = "dummyValue"
        val dest = S3Destination(S3DestinationConfigFactory(), envWithBadExternalId)
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.FAILED,
            dest.check(S3DestinationTestUtils.assumeRoleConfig)!!.status
        )
    }

    // This test is a bit hairy. We assume a role, and then create a policy that denies ALL for any
    // token that were created before now().
    // This effectively cancels the token created above.
    // Then we double check that the deny policy is applied, and then explicitely call refresh, to
    // make
    // sure
    // the token gets renewed. In a real prod case, the refresh is called by a background thread
    @Test
    @Timeout(value = 1, unit = TimeUnit.HOURS)
    @Throws(InterruptedException::class)
    fun testAutomaticRenewal() {
        val iam =
            AmazonIdentityManagementClientBuilder.standard()
                .withRegion(Regions.DEFAULT_REGION)
                .withCredentials(
                    S3AssumeRoleCredentialConfig.getCredentialProvider(
                        S3DestinationTestUtils.policyManagerCredentials
                    )
                )
                .build()
        val listPoliciesRequest = ListAttachedRolePoliciesRequest().withRoleName(ASSUMED_ROLE_NAME)
        val policies = iam.listAttachedRolePolicies(listPoliciesRequest).attachedPolicies
        // We start deleting old deny policies that this test instance might have created. Just
        // making sure
        // our S3 policies are reasonable
        for (policy in policies) {
            val policyName = policy.policyName
            if (policyName.startsWith(POLICY_NAME_PREFIX)) {
                val policyCreationDateString =
                    policyName.substring(POLICY_NAME_PREFIX.length).replace('_', ':')
                if (
                    Instant.parse(policyCreationDateString)
                        .isBefore(Instant.now().minus(1, ChronoUnit.DAYS))
                ) {
                    val detachPolicyRequest =
                        DetachRolePolicyRequest()
                            .withPolicyArn(policy.policyArn)
                            .withRoleName(ASSUMED_ROLE_NAME)
                    iam.detachRolePolicy(detachPolicyRequest)
                    val deleteRequest = DeletePolicyRequest().withPolicyArn(policy.policyArn)
                    iam.deletePolicy(deleteRequest)
                }
            }
        }

        val environmentForAssumeRole = S3DestinationTestUtils.assumeRoleInternalCredentials
        val config: S3DestinationConfig =
            S3DestinationConfig.getS3DestinationConfig(
                S3DestinationTestUtils.assumeRoleConfig,
                environmentForAssumeRole
            )
        val s3Client = config.getS3Client()
        testSingleUpload(s3Client, config.bucketName, config.bucketPath!!)

        // We wait 1 second so that the less than is strictly greater than the token generation time
        Thread.sleep(1000)
        val now = Instant.now().truncatedTo(ChronoUnit.SECONDS).toString()
        val policyName = POLICY_NAME_PREFIX + now.toString().replace(':', '_')

        val policyDocument = REVOKE_OLD_TOKENS_POLICY.format(now)
        val createPolicyRequest =
            CreatePolicyRequest().withPolicyName(policyName).withPolicyDocument(policyDocument)
        val arn = iam.createPolicy(createPolicyRequest).policy.arn
        try {
            val attachPolicyRequest =
                AttachRolePolicyRequest().withRoleName(ASSUMED_ROLE_NAME).withPolicyArn(arn)

            iam.attachRolePolicy(attachPolicyRequest)
            // Experience showed than under 30sec, the policy is not applied. Giving it some buffer
            Thread.sleep(60000)

            // We check that the deny policy is enforced
            Assertions.assertThrows(Exception::class.java) {
                testSingleUpload(s3Client, config.bucketName, config.bucketPath!!)
            }
            // and force-refresh the token
            config.s3CredentialConfig!!.s3CredentialsProvider.refresh()
            testSingleUpload(s3Client, config.bucketName, config.bucketPath!!)
        } finally {
            val detachPolicyRequest =
                DetachRolePolicyRequest().withPolicyArn(arn).withRoleName(ASSUMED_ROLE_NAME)
            iam.detachRolePolicy(detachPolicyRequest)
            val deleteRequest = DeletePolicyRequest().withPolicyArn(arn)
            iam.deletePolicy(deleteRequest)
        }
    }

    companion object {
        private val REVOKE_OLD_TOKENS_POLICY =
            """
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
                                                         
                                                         """.trimIndent()
        private val POLICY_NAME_PREFIX =
            S3DestinationAssumeRoleTest::class.java.simpleName + "Policy-"
        private const val ASSUMED_ROLE_NAME = "s3_acceptance_test_iam_assume_role_role"
    }
}

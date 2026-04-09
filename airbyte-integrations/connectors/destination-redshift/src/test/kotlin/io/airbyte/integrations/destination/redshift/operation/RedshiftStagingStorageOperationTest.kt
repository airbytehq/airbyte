/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.operation

import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.auth.BasicSessionCredentials
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialType
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class RedshiftStagingStorageOperationTest {

    private fun createOperation(
        credentialConfig: S3CredentialConfig,
        iamRoleArn: String? = null,
    ): RedshiftStagingStorageOperation {
        val s3Config = mock(S3DestinationConfig::class.java)
        `when`(s3Config.s3CredentialConfig).thenReturn(credentialConfig)

        return RedshiftStagingStorageOperation(
            s3Config,
            keepStagingFiles = false,
            mock(S3StorageOperations::class.java),
            mock(RedshiftSqlGenerator::class.java),
            mock(RedshiftDestinationHandler::class.java),
            dropCascade = false,
            iamRoleArn = iamRoleArn,
        )
    }

    @Test
    fun testBuildCredentialClauseWithAccessKey() {
        val credentialConfig = S3AccessKeyCredentialConfig(
            "AKIAIOSFODNN7EXAMPLE",
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
        val operation = createOperation(credentialConfig)

        val clause = operation.buildCredentialClause()

        assertEquals(
            "CREDENTIALS 'aws_access_key_id=AKIAIOSFODNN7EXAMPLE;aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'",
            clause
        )
    }

    @Test
    fun testBuildCredentialClauseWithIamRoleDefault() {
        val credentialConfig = mock(S3CredentialConfig::class.java)
        `when`(credentialConfig.credentialType).thenReturn(S3CredentialType.DEFAULT_PROFILE)

        val operation = createOperation(credentialConfig, iamRoleArn = null)

        val clause = operation.buildCredentialClause()

        assertEquals("IAM_ROLE default", clause)
    }

    @Test
    fun testBuildCredentialClauseWithExplicitIamRoleArn() {
        val credentialConfig = mock(S3CredentialConfig::class.java)
        `when`(credentialConfig.credentialType).thenReturn(S3CredentialType.DEFAULT_PROFILE)

        val operation = createOperation(
            credentialConfig,
            iamRoleArn = "arn:aws:iam::123456789012:role/redshift-s3-read"
        )

        val clause = operation.buildCredentialClause()

        assertEquals("IAM_ROLE 'arn:aws:iam::123456789012:role/redshift-s3-read'", clause)
    }

    @Test
    fun testRejectsInvalidArnAtConstructionTime() {
        val credentialConfig = mock(S3CredentialConfig::class.java)
        `when`(credentialConfig.credentialType).thenReturn(S3CredentialType.DEFAULT_PROFILE)

        assertThrows(IllegalArgumentException::class.java) {
            createOperation(
                credentialConfig,
                iamRoleArn = "not-a-valid-arn"
            )
        }
    }

    @Test
    fun testBuildCredentialClauseWithAssumeRoleAndSessionToken() {
        val sessionCreds = BasicSessionCredentials(
            "ASIATEMP", "tempSecret", "sessionToken123"
        )
        val provider: AWSCredentialsProvider = AWSStaticCredentialsProvider(sessionCreds)

        val credentialConfig = mock(S3CredentialConfig::class.java)
        `when`(credentialConfig.credentialType).thenReturn(S3CredentialType.ASSUME_ROLE)
        `when`(credentialConfig.s3CredentialsProvider).thenReturn(provider)

        val operation = createOperation(credentialConfig)

        val clause = operation.buildCredentialClause()

        assertTrue(clause.contains("token=sessionToken123"))
        assertTrue(clause.contains("aws_access_key_id=ASIATEMP"))
    }

    @Test
    fun testBuildCredentialClauseWithAssumeRoleWithoutSessionToken() {
        val basicCreds = BasicAWSCredentials("ASIANONSESSION", "nonSessionSecret")
        val provider: AWSCredentialsProvider = AWSStaticCredentialsProvider(basicCreds)

        val credentialConfig = mock(S3CredentialConfig::class.java)
        `when`(credentialConfig.credentialType).thenReturn(S3CredentialType.ASSUME_ROLE)
        `when`(credentialConfig.s3CredentialsProvider).thenReturn(provider)

        val operation = createOperation(credentialConfig)

        val clause = operation.buildCredentialClause()

        assertEquals(
            "CREDENTIALS 'aws_access_key_id=ASIANONSESSION;aws_secret_access_key=nonSessionSecret'",
            clause
        )
    }

    @Test
    fun testBuildCredentialClauseAccessKeyTakesPrecedenceOverIamRoleArn() {
        val credentialConfig = S3AccessKeyCredentialConfig(
            "AKIAIOSFODNN7EXAMPLE",
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
        val operation = createOperation(
            credentialConfig,
            iamRoleArn = "arn:aws:iam::123456789012:role/should-be-ignored"
        )

        val clause = operation.buildCredentialClause()

        assertTrue(clause.startsWith("CREDENTIALS '"))
        assertTrue(clause.contains("aws_access_key_id=AKIAIOSFODNN7EXAMPLE"))
    }
}

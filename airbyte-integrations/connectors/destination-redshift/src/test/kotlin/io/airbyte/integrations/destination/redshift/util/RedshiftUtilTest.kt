/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.UPLOADING_METHOD
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil.anyOfS3FieldsAreNullOrEmpty
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil.findS3Options
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class RedshiftUtilTest {
    @Test
    @DisplayName("Should return the config when the config has uploading method")
    fun testFindS3OptionsWhenConfigHasUploadingMethod() {
        val config = Mockito.mock(JsonNode::class.java)
        val uploadingMethod = Mockito.mock(JsonNode::class.java)
        Mockito.`when`<Boolean>(config.has(UPLOADING_METHOD)).thenReturn(true)
        Mockito.`when`<JsonNode>(config.get(UPLOADING_METHOD)).thenReturn(uploadingMethod)

        val result = findS3Options(config)

        Assertions.assertEquals(uploadingMethod, result)
    }

    @Test
    @DisplayName("Should return the config when the config does not have uploading method")
    fun testFindS3OptionsWhenConfigDoesNotHaveUploadingMethod() {
        val config = Mockito.mock(JsonNode::class.java)
        Mockito.`when`<Boolean>(config.has(UPLOADING_METHOD)).thenReturn(false)

        val result = findS3Options(config)

        Assertions.assertEquals(config, result)
    }

    @Test
    @DisplayName("Should return true when all of the fields are null or empty")
    fun testAnyOfS3FieldsAreNullOrEmptyWhenAllOfTheFieldsAreNullOrEmptyThenReturnTrue() {
        val jsonNode = Mockito.mock(JsonNode::class.java)
        Mockito.`when`(jsonNode["s3_bucket_name"]).thenReturn(null)
        Mockito.`when`(jsonNode["s3_bucket_region"]).thenReturn(null)
        Mockito.`when`(jsonNode["access_key_id"]).thenReturn(null)
        Mockito.`when`(jsonNode["secret_access_key"]).thenReturn(null)

        Assertions.assertTrue(anyOfS3FieldsAreNullOrEmpty(jsonNode))
    }

    @Test
    @DisplayName("Should return false when all S3 required fields are not null or empty")
    fun testAllS3RequiredAreNotNullOrEmptyThenReturnFalse() {
        val jsonNode = Mockito.mock(JsonNode::class.java)
        Mockito.`when`(jsonNode["s3_bucket_name"]).thenReturn(Mockito.mock(JsonNode::class.java))
        Mockito.`when`(jsonNode["s3_bucket_name"].asText()).thenReturn("test")
        Mockito.`when`(jsonNode["s3_bucket_region"]).thenReturn(Mockito.mock(JsonNode::class.java))
        Mockito.`when`(jsonNode["s3_bucket_region"].asText()).thenReturn("test")
        Mockito.`when`(jsonNode["access_key_id"]).thenReturn(Mockito.mock(JsonNode::class.java))
        Mockito.`when`(jsonNode["access_key_id"].asText()).thenReturn("test")
        Mockito.`when`(jsonNode["secret_access_key"]).thenReturn(Mockito.mock(JsonNode::class.java))
        Mockito.`when`(jsonNode["secret_access_key"].asText()).thenReturn("test")

        Assertions.assertFalse(anyOfS3FieldsAreNullOrEmpty(jsonNode))
    }
}

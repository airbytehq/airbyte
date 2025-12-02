/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import io.airbyte.cdk.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import java.io.IOException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class GcsDestinationConfigTest {
    @Test
    @Throws(IOException::class)
    fun testGetGcsDestinationConfig() {
        val configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"))

        val config = GcsDestinationConfig.getGcsDestinationConfig(configJson)
        Assertions.assertEquals("test_bucket", config.bucketName)
        Assertions.assertEquals("test_path", config.bucketPath)
        Assertions.assertEquals("us-west1", config.bucketRegion)

        val credentialConfig = config.gcsCredentialConfig
        Assertions.assertTrue(credentialConfig is GcsHmacKeyCredentialConfig)

        val hmacKeyConfig = credentialConfig as GcsHmacKeyCredentialConfig
        Assertions.assertEquals("test_access_id", hmacKeyConfig.hmacKeyAccessId)
        Assertions.assertEquals("test_secret", hmacKeyConfig.hmacKeySecret)

        val formatConfig = config.formatConfig
        Assertions.assertTrue(formatConfig is UploadAvroFormatConfig)

        val avroFormatConfig = formatConfig as UploadAvroFormatConfig
        Assertions.assertEquals("deflate-5", avroFormatConfig.codecFactory.toString())
    }
}

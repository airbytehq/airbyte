/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.regex.Pattern
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class SnowflakeDestinationTest {
    @BeforeEach
    fun setup() {
        DestinationConfig.initialize(emptyObject())
    }

    @ParameterizedTest
    @MethodSource("urlsDataProvider")
    @Throws(Exception::class)
    fun testUrlPattern(url: String?, isMatch: Boolean) {
        val spec = SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).spec()
        val pattern =
            Pattern.compile(spec.connectionSpecification["properties"]["host"]["pattern"].asText())

        val matcher = pattern.matcher(url)
        Assertions.assertEquals(isMatch, matcher.find())
    }

    @Test
    @Throws(Exception::class)
    fun testWriteSnowflakeInternal() {
        val config = deserialize(readResource("internal_staging_config.json"), JsonNode::class.java)
        val consumer =
            SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).getSerializedMessageConsumer(
                config,
                ConfiguredAirbyteCatalog()
            ) { _: AirbyteMessage? -> }
        Assertions.assertEquals(AsyncStreamConsumer::class.java, consumer.javaClass)
    }

    companion object {
        @JvmStatic
        private fun urlsDataProvider(): Stream<Arguments> {
            return Stream
                .of( // See https://docs.snowflake.com/en/user-guide/admin-account-identifier for
                    // specific requirements
                    // "Account name in organization" style
                    Arguments.arguments(
                        "https://acme-marketing-test-account.snowflakecomputing.com",
                        true
                    ),
                    Arguments.arguments(
                        "https://acme-marketing_test_account.snowflakecomputing.com",
                        true
                    ),
                    Arguments.arguments(
                        "https://acme-marketing.test-account.snowflakecomputing.com",
                        true
                    ), // Legacy style (account locator in a region)
                    // Some examples taken from
                    // https://docs.snowflake.com/en/user-guide/admin-account-identifier#non-vps-account-locator-formats-by-cloud-platform-and-region

                    Arguments.arguments("xy12345.snowflakecomputing.com", true),
                    Arguments.arguments("xy12345.us-gov-west-1.aws.snowflakecomputing.com", true),
                    Arguments.arguments(
                        "xy12345.us-east-1.aws.snowflakecomputing.com",
                        true
                    ), // And some other formats which are, de facto, valid
                    Arguments.arguments("xy12345.foo.us-west-2.aws.snowflakecomputing.com", true),
                    Arguments.arguments("https://xy12345.snowflakecomputing.com", true),
                    Arguments.arguments("https://xy12345.us-east-1.snowflakecomputing.com", true),
                    Arguments.arguments(
                        "https://xy12345.us-east-1.aws.snowflakecomputing.com",
                        true
                    ),
                    Arguments.arguments(
                        "https://xy12345.foo.us-west-2.aws.snowflakecomputing.com",
                        true
                    ), // Invalid formats
                    Arguments.arguments("example.snowflakecomputing.com/path/to/resource", false),
                    Arguments.arguments("example.snowflakecomputing.com:8080", false),
                    Arguments.arguments("example.snowflakecomputing.com:12345", false),
                    Arguments.arguments("example.snowflakecomputing.com//path/to/resource", false),
                    Arguments.arguments("example.snowflakecomputing.com/path?query=string", false),
                    Arguments.arguments("example.snowflakecomputing.com/#fragment", false),
                    Arguments.arguments("ab12345.us-east-2.aws.snowflakecomputing. com", false),
                    Arguments.arguments("ab12345.us-east-2.aws.snowflakecomputing..com", false)
                )
        }
    }
}

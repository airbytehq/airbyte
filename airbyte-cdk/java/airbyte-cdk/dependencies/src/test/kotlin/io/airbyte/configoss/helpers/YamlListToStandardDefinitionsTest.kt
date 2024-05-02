/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss.helpers

import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.configoss.StandardDestinationDefinition
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

internal class YamlListToStandardDefinitionsTest {
    @Nested
    internal inner class VerifyAndConvertToJsonNode {
        private val mapper: ObjectMapper = MoreMappers.initMapper()

        @Test
        @Throws(JsonProcessingException::class)
        fun correctlyReadTest() {
            val jsonDefs =
                YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, GOOD_DES_DEF_YAML)
            val defList =
                mapper.treeToValue(jsonDefs, Array<StandardDestinationDefinition>::class.java)
            Assertions.assertEquals(1, defList.size)
            Assertions.assertEquals("Local JSON", defList[0].name)
        }

        @Test
        fun duplicateIdTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, DUPLICATE_ID)
            }
        }

        @Test
        fun duplicateNameTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, DUPLICATE_NAME)
            }
        }

        @Test
        fun emptyFileTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, "")
            }
        }

        @Test
        fun badDataTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, BAD_DATA)
            }
        }
    }

    @Nested
    internal inner class VerifyAndConvertToModelList {
        @Test
        fun correctlyReadTest() {
            val defs =
                YamlListToStandardDefinitions.verifyAndConvertToModelList(
                    StandardDestinationDefinition::class.java,
                    GOOD_DES_DEF_YAML
                )
            Assertions.assertEquals(1, defs.size)
            Assertions.assertEquals("Local JSON", defs[0]!!.name)
        }

        @Test
        fun duplicateIdTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToModelList(
                    StandardDestinationDefinition::class.java,
                    DUPLICATE_ID
                )
            }
        }

        @Test
        fun duplicateNameTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToModelList(
                    StandardDestinationDefinition::class.java,
                    DUPLICATE_NAME
                )
            }
        }

        @Test
        fun emptyFileTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToModelList(
                    StandardDestinationDefinition::class.java,
                    ""
                )
            }
        }

        @Test
        fun badDataTest() {
            Assertions.assertThrows(RuntimeException::class.java) {
                YamlListToStandardDefinitions.verifyAndConvertToModelList(
                    StandardDestinationDefinition::class.java,
                    BAD_DATA
                )
            }
        }
    }

    companion object {
        private const val DESTINATION_DEFINITION_ID =
            "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n"
        private const val DESTINATION_NAME = "  name: Local JSON\n"
        private const val DOCKER_REPO = "  dockerRepository: airbyte/destination-local-json\n"
        private const val DOCKER_IMAGE_TAG = "  dockerImageTag: 0.1.4\n"
        private const val GOOD_DES_DEF_YAML =
            (DESTINATION_DEFINITION_ID +
                DESTINATION_NAME +
                DOCKER_REPO +
                DOCKER_IMAGE_TAG +
                "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json")
        private const val DUPLICATE_ID =
            """$DESTINATION_DEFINITION_ID$DESTINATION_NAME$DOCKER_REPO$DOCKER_IMAGE_TAG  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json$DESTINATION_DEFINITION_ID  name: JSON 2
$DOCKER_REPO$DOCKER_IMAGE_TAG  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json"""
        private const val DUPLICATE_NAME =
            """$DESTINATION_DEFINITION_ID$DESTINATION_NAME$DOCKER_REPO$DOCKER_IMAGE_TAG  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json
- destinationDefinitionId: 8be1cf83-fde1-477f-a4ad-318d23c9f3c6
$DESTINATION_NAME  dockerRepository: airbyte/destination-csv
  dockerImageTag: 0.1.8
  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-csv"""
        private const val BAD_DATA =
            """$DESTINATION_DEFINITION_ID$DESTINATION_NAME$DOCKER_REPO  dockerImageTag: 0.1.8
  documentationUrl"""
        private const val ID_NAME = "destinationDefinitionId"
    }
}

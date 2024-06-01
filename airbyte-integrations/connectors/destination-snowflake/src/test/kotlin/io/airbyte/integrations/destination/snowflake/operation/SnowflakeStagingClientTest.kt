/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.mockk.confirmVerified
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import io.mockk.verifySequence
import java.io.File
import java.lang.RuntimeException
import java.sql.SQLException
import java.util.stream.Stream
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class SnowflakeStagingClientTest {

    @Nested
    inner class SuccessTest {
        private val database =
            mockk<JdbcDatabase>(relaxed = true, relaxUnitFun = true) {
                // checkIfStage exists should be the only call to mock. it checks if any object
                // exists.
                every { unsafeQuery(any()) } returns listOf(Jsons.emptyObject()).stream()
            }
        private val stagingClient = SnowflakeStagingClient(database)

        @Test
        fun verifyUploadRecordsToStage() {
            val mockFileName = "mock-file-name"
            val mockFileAbsolutePath = "/tmp/$mockFileName"
            val recordBuffer =
                mockk<SerializableBuffer>() {
                    every { filename } returns mockFileName
                    every { file } returns
                        mockk<File>() { every { absolutePath } returns mockFileAbsolutePath }
                }
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"

            val putQuery = stagingClient.getPutQuery(stageName, stagingPath, mockFileAbsolutePath)
            val listQuery = stagingClient.getListQuery(stageName, stagingPath, mockFileName)
            val stagedFile =
                stagingClient.uploadRecordsToStage(recordBuffer, stageName, stagingPath)
            assertEquals(stagedFile, mockFileName)
            verify {
                database.execute(putQuery)
                database.unsafeQuery(listQuery)
            }
            confirmVerified(database)
        }

        @Test
        fun verifyCreateStageIfNotExists() {
            val stageName = "dummy"
            stagingClient.createStageIfNotExists(stageName)
            verify { database.execute(stagingClient.getCreateStageQuery(stageName)) }
            confirmVerified(database)
        }

        @Test
        fun verifyCopyIntoTableFromStage() {
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"
            val stagedFiles = listOf("mock-file-name")
            stagingClient.copyIntoTableFromStage(stageName, stagingPath, stagedFiles, streamId)
            verify {
                database.execute(
                    stagingClient.getCopyQuery(stageName, stagingPath, stagedFiles, streamId)
                )
            }
            confirmVerified(database)
        }

        @Test
        fun verifyDropStageIfExists() {
            val stageName = "dummy"
            stagingClient.dropStageIfExists(stageName)
            verify { database.execute(stagingClient.getDropQuery(stageName)) }
            confirmVerified(database)
        }
    }

    @Nested
    inner class FailureTest {

        @Test
        fun verifyUploadToStageRetriedOnFileNotFound() {
            val database =
                mockk<JdbcDatabase>(relaxed = true, relaxUnitFun = true) {
                    // throw exception first on execute and success
                    every { execute(any(String::class)) } returns Unit
                    // return empty stream on first checkStage and then some data
                    every { unsafeQuery(any()) } returns listOf<JsonNode>().stream()
                }
            val stagingClient = SnowflakeStagingClient(database)

            val mockFileName = "mock-file-name"
            val mockFileAbsolutePath = "/tmp/$mockFileName"
            val recordBuffer =
                mockk<SerializableBuffer>() {
                    every { filename } returns mockFileName
                    every { file } returns
                        mockk<File>() { every { absolutePath } returns mockFileAbsolutePath }
                }
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"

            val putQuery = stagingClient.getPutQuery(stageName, stagingPath, mockFileAbsolutePath)
            val listQuery = stagingClient.getListQuery(stageName, stagingPath, mockFileName)
            assertThrows(RuntimeException::class.java) {
                stagingClient.uploadRecordsToStage(recordBuffer, stageName, stagingPath)
            }
            verify(exactly = 3) {
                database.execute(putQuery)
                database.unsafeQuery(listQuery)
            }
            confirmVerified(database)
        }

        @Test
        fun verifyUploadToStageRetriedOnException() {
            val database =
                mockk<JdbcDatabase>(relaxed = true, relaxUnitFun = true) {
                    // throw exception first on execute and success
                    every { execute(any(String::class)) } throws
                        SQLException("Query can't be executed")
                }
            val stagingClient = SnowflakeStagingClient(database)

            val mockFileName = "mock-file-name"
            val mockFileAbsolutePath = "/tmp/$mockFileName"
            val recordBuffer =
                mockk<SerializableBuffer> {
                    every { filename } returns mockFileName
                    every { file } returns
                        mockk<File>() { every { absolutePath } returns mockFileAbsolutePath }
                }
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"

            val putQuery = stagingClient.getPutQuery(stageName, stagingPath, mockFileAbsolutePath)
            assertThrows(RuntimeException::class.java) {
                stagingClient.uploadRecordsToStage(recordBuffer, stageName, stagingPath)
            }
            verifySequence {
                database.execute(putQuery)
                database.execute(putQuery)
                database.execute(putQuery)
            }
            confirmVerified(database)
        }

        @ParameterizedTest(name = ParameterizedTest.ARGUMENTS_WITH_NAMES_PLACEHOLDER)
        @MethodSource(
            "io.airbyte.integrations.destination.snowflake.operation.SnowflakeStagingClientTest#argumentsForCheckKnownExceptionCaught"
        )
        fun verifyKnownExceptionConvertedToConfigException(
            isCaptured: Boolean,
            executable: Executable
        ) {
            if (isCaptured) {
                assertThrows(ConfigErrorException::class.java, executable)
            } else {
                assertThrows(SnowflakeSQLException::class.java, executable)
            }
        }
    }

    companion object {
        private const val UNKNOWN_EXCEPTION_MESSAGE = "Unknown Exception"
        private const val PERMISSION_EXCEPTION_PARTIAL_MSG =
            "but current role has no privileges on it"
        private const val IP_NOT_IN_WHITE_LIST_EXCEPTION_PARTIAL_MSG =
            "not allowed to access Snowflake"

        val streamId =
            StreamId(
                "final_namespace",
                "final_name",
                "raw_namespace",
                "raw_name",
                "original_namespace",
                "original_name",
            )

        @JvmStatic
        fun argumentsForCheckKnownExceptionCaught(): Stream<Arguments> {
            val mockStageName = "dummy-stage-name"
            val mockStagingPath = "2024/uuid-random"
            val mockFileName = "mock-file-name"
            return Stream.of(
                Arguments.of(
                    false,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                UNKNOWN_EXCEPTION_MESSAGE,
                            )
                            .createStageIfNotExists(mockStageName)
                    },
                ),
                Arguments.of(
                    true,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                IP_NOT_IN_WHITE_LIST_EXCEPTION_PARTIAL_MSG,
                            )
                            .createStageIfNotExists(mockStageName)
                    },
                ),
                Arguments.of(
                    true,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(PERMISSION_EXCEPTION_PARTIAL_MSG)
                            .createStageIfNotExists(mockStageName)
                    }
                ),
                Arguments.of(
                    false,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                UNKNOWN_EXCEPTION_MESSAGE,
                            )
                            .copyIntoTableFromStage(
                                mockStageName,
                                mockStagingPath,
                                listOf(mockFileName),
                                streamId
                            )
                    },
                ),
                Arguments.of(
                    true,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                IP_NOT_IN_WHITE_LIST_EXCEPTION_PARTIAL_MSG,
                            )
                            .copyIntoTableFromStage(
                                mockStageName,
                                mockStagingPath,
                                listOf(mockFileName),
                                streamId
                            )
                    },
                ),
                Arguments.of(
                    true,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                PERMISSION_EXCEPTION_PARTIAL_MSG,
                            )
                            .copyIntoTableFromStage(
                                mockStageName,
                                mockStagingPath,
                                listOf(mockFileName),
                                streamId
                            )
                    },
                ),
                Arguments.of(
                    false,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                UNKNOWN_EXCEPTION_MESSAGE,
                            )
                            .dropStageIfExists(mockStageName)
                    },
                ),
                Arguments.of(
                    true,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                IP_NOT_IN_WHITE_LIST_EXCEPTION_PARTIAL_MSG,
                            )
                            .dropStageIfExists(mockStageName)
                    },
                ),
                Arguments.of(
                    true,
                    Executable {
                        getMockedStagingClientWithExceptionThrown(
                                PERMISSION_EXCEPTION_PARTIAL_MSG,
                            )
                            .dropStageIfExists(mockStageName)
                    },
                ),
            )
        }

        private fun getMockedStagingClientWithExceptionThrown(
            exceptionMessage: String
        ): SnowflakeStagingClient {
            val database =
                mockk<JdbcDatabase>(relaxed = true, relaxUnitFun = true) {
                    // throw exception first on execute and success
                    every { execute(any(String::class)) } throws
                        SnowflakeSQLException(exceptionMessage)
                }
            return SnowflakeStagingClient(database)
        }
    }
}

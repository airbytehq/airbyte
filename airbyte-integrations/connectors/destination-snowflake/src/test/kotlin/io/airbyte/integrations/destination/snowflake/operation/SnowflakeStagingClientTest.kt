/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.operation

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.io.File
import java.sql.SQLException
import java.util.stream.Stream
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.mockito.kotlin.any
import org.mockito.kotlin.doNothing
import org.mockito.kotlin.doThrow
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.reset
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.verifyNoMoreInteractions
import org.mockito.kotlin.whenever

@SuppressFBWarnings("BC_IMPOSSIBLE_CAST")
class SnowflakeStagingClientTest {

    @Nested
    inner class SuccessTest {
        private val database = mock<JdbcDatabase>()
        private val stagingClient = SnowflakeStagingClient(database)

        @BeforeEach
        fun setUp() {
            // checkIfStage exists should be the only call to mock. it checks if any object
            // exists.
            whenever(database.unsafeQuery(any())).thenReturn(listOf(Jsons.emptyObject()).stream())
        }

        @AfterEach
        fun tearDown() {
            reset(database)
        }

        @Test
        fun verifyUploadRecordsToStage() {
            val mockFileName = "mock-file-name"
            val mockFileAbsolutePath = "/tmp/$mockFileName"
            val mockFile = mock<File> { whenever(it.absolutePath).thenReturn(mockFileAbsolutePath) }
            val recordBuffer =
                mock<SerializableBuffer>() {
                    whenever(it.filename).thenReturn(mockFileName)
                    whenever(it.file).thenReturn(mockFile)
                }

            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"

            val putQuery = stagingClient.getPutQuery(stageName, stagingPath, mockFileAbsolutePath)
            val listQuery = stagingClient.getListQuery(stageName, stagingPath, mockFileName)
            val stagedFile =
                stagingClient.uploadRecordsToStage(recordBuffer, stageName, stagingPath)
            assertEquals(stagedFile, mockFileName)
            val inOrder = inOrder(database)
            inOrder.verify(database).execute(putQuery)
            inOrder.verify(database).unsafeQuery(listQuery)
            verifyNoMoreInteractions(database)
        }

        @Test
        fun verifyCreateStageIfNotExists() {
            val stageName = "dummy"
            stagingClient.createStageIfNotExists(stageName)
            val inOrder = inOrder(database)
            inOrder.verify(database).execute(stagingClient.getCreateStageQuery(stageName))
            verifyNoMoreInteractions(database)
        }

        @Test
        fun verifyCopyIntoTableFromStage() {
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"
            val stagedFiles = listOf("mock-file-name")
            stagingClient.copyIntoTableFromStage(stageName, stagingPath, stagedFiles, streamId)
            val inOrder = inOrder(database)
            inOrder
                .verify(database)
                .execute(stagingClient.getCopyQuery(stageName, stagingPath, stagedFiles, streamId))
            verifyNoMoreInteractions(database)
        }

        @Test
        fun verifyDropStageIfExists() {
            val stageName = "dummy"
            stagingClient.dropStageIfExists(stageName)
            val inOrder = inOrder(database)
            inOrder.verify(database).execute(stagingClient.getDropQuery(stageName))
            verifyNoMoreInteractions(database)
        }
    }

    @Nested
    inner class FailureTest {

        @Test
        fun verifyUploadToStageRetriedOnFileNotFound() {
            val database =
                mock<JdbcDatabase>() {
                    doNothing().whenever(it).execute(any<String>())
                    whenever(it.unsafeQuery(any<String>())).thenReturn(listOf<JsonNode>().stream())
                }
            val stagingClient = SnowflakeStagingClient(database)

            val mockFileName = "mock-file-name"
            val mockFileAbsolutePath = "/tmp/$mockFileName"
            val mockFile =
                mock<File> { file -> whenever(file.absolutePath).thenReturn(mockFileAbsolutePath) }
            val recordBuffer =
                mock<SerializableBuffer> {
                    whenever(it.filename).thenReturn(mockFileName)
                    whenever(it.file).thenReturn(mockFile)
                }
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"

            val putQuery = stagingClient.getPutQuery(stageName, stagingPath, mockFileAbsolutePath)
            val listQuery = stagingClient.getListQuery(stageName, stagingPath, mockFileName)
            assertThrows(RuntimeException::class.java) {
                stagingClient.uploadRecordsToStage(recordBuffer, stageName, stagingPath)
            }
            verify(database, times(3)).execute(putQuery)
            verify(database, times(3)).unsafeQuery(listQuery)
            verifyNoMoreInteractions(database)
        }

        @Test
        fun verifyUploadToStageRetriedOnException() {
            val database =
                mock<JdbcDatabase>() {
                    doThrow(SQLException("Query can't be executed"))
                        .whenever(it)
                        .execute(any<String>())
                }
            val stagingClient = SnowflakeStagingClient(database)

            val mockFileName = "mock-file-name"
            val mockFileAbsolutePath = "/tmp/$mockFileName"
            val mockFile =
                mock<File> { file -> whenever(file.absolutePath).thenReturn(mockFileAbsolutePath) }
            val recordBuffer =
                mock<SerializableBuffer> {
                    whenever(it.filename).thenReturn(mockFileName)
                    whenever(it.file).thenReturn(mockFile)
                }
            val stageName = "dummy"
            val stagingPath = "2024/uuid-random"

            val putQuery = stagingClient.getPutQuery(stageName, stagingPath, mockFileAbsolutePath)
            assertThrows(RuntimeException::class.java) {
                stagingClient.uploadRecordsToStage(recordBuffer, stageName, stagingPath)
            }
            verify(database, times(3)).execute(putQuery)
            verifyNoMoreInteractions(database)
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
                mock<JdbcDatabase> {
                    doThrow(SnowflakeSQLException(exceptionMessage))
                        .whenever(it)
                        .execute(any<String>())
                }
            return SnowflakeStagingClient(database)
        }
    }
}

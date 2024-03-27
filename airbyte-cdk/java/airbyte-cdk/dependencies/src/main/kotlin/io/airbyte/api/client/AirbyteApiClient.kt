/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.api.client

import com.google.common.annotations.VisibleForTesting
import io.airbyte.api.client.generated.*
import io.airbyte.api.client.invoker.generated.ApiClient
import java.util.*
import java.util.concurrent.Callable
import kotlin.math.max
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This class is meant to consolidate all our API endpoints into a fluent-ish client. Currently, all
 * open API generators create a separate class per API "root-route". For example, if our API has two
 * routes "/v1/First/get" and "/v1/Second/get", OpenAPI generates (essentially) the following files:
 *
 * ApiClient.java, FirstApi.java, SecondApi.java
 *
 * To call the API type-safely, we'd do new FirstApi(new ApiClient()).get() or new SecondApi(new
 * ApiClient()).get(), which can get cumbersome if we're interacting with many pieces of the API.
 *
 * This is currently manually maintained. We could look into autogenerating it if needed.
 */
class AirbyteApiClient(apiClient: ApiClient) {
    val connectionApi: ConnectionApi = ConnectionApi(apiClient)
    val destinationDefinitionApi: DestinationDefinitionApi = DestinationDefinitionApi(apiClient)
    val destinationApi: DestinationApi = DestinationApi(apiClient)
    val destinationDefinitionSpecificationApi: DestinationDefinitionSpecificationApi =
        DestinationDefinitionSpecificationApi(apiClient)
    val jobsApi: JobsApi = JobsApi(apiClient)
    val logsApi: PatchedLogsApi = PatchedLogsApi(apiClient)
    val operationApi: OperationApi = OperationApi(apiClient)
    val sourceDefinitionApi: SourceDefinitionApi = SourceDefinitionApi(apiClient)
    val sourceApi: SourceApi = SourceApi(apiClient)
    val sourceDefinitionSpecificationApi: SourceDefinitionSpecificationApi =
        SourceDefinitionSpecificationApi(apiClient)
    val workspaceApi: WorkspaceApi = WorkspaceApi(apiClient)
    val healthApi: HealthApi = HealthApi(apiClient)
    val attemptApi: AttemptApi = AttemptApi(apiClient)
    val stateApi: StateApi = StateApi(apiClient)

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(AirbyteApiClient::class.java)
        private val RANDOM = Random()

        const val DEFAULT_MAX_RETRIES: Int = 4
        const val DEFAULT_RETRY_INTERVAL_SECS: Int = 10
        const val DEFAULT_FINAL_INTERVAL_SECS: Int = 10 * 60

        /**
         * Default to 4 retries with a randomised 1 - 10 seconds interval between the first two
         * retries and an 10-minute wait for the last retry.
         */
        fun <T> retryWithJitter(call: Callable<T>, desc: String?): T? {
            return retryWithJitter(
                call,
                desc,
                DEFAULT_RETRY_INTERVAL_SECS,
                DEFAULT_FINAL_INTERVAL_SECS,
                DEFAULT_MAX_RETRIES
            )
        }

        /**
         * Provides a simple retry wrapper for api calls. This retry behaviour is slightly different
         * from generally available retries libraries - the last retry is able to wait an interval
         * inconsistent with regular intervals/exponential backoff.
         *
         * Since the primary retries use case is long-running workflows, the benefit of waiting a
         * couple of minutes as a last ditch effort to outlast networking disruption outweighs the
         * cost of slightly longer jobs.
         *
         * @param call method to execute
         * @param desc short readable explanation of why this method is executed
         * @param jitterMaxIntervalSecs upper limit of the randomised retry interval. Minimum value
         * is 1.
         * @param finalIntervalSecs retry interval before the last retry.
         */
        @VisibleForTesting // This is okay since we are logging the stack trace, which PMD is not
        // detecting.
        fun <T> retryWithJitter(
            call: Callable<T>,
            desc: String?,
            jitterMaxIntervalSecs: Int,
            finalIntervalSecs: Int,
            maxTries: Int
        ): T? {
            var currRetries = 0
            var keepTrying = true

            while (keepTrying && currRetries < maxTries) {
                try {
                    LOGGER.info("Attempt {} to {}", currRetries, desc)
                    return call.call()

                    keepTrying = false
                } catch (e: Exception) {
                    LOGGER.info("Attempt {} to {} error: {}", currRetries, desc, e)
                    currRetries++

                    // Sleep anywhere from 1 to jitterMaxIntervalSecs seconds.
                    val backoffTimeSecs =
                        max(RANDOM.nextInt(jitterMaxIntervalSecs + 1).toDouble(), 1.0).toInt()
                    var backoffTimeMs = backoffTimeSecs * 1000

                    if (currRetries == maxTries - 1) {
                        // sleep for finalIntervalMins on the last attempt.
                        backoffTimeMs = finalIntervalSecs * 1000
                    }

                    try {
                        Thread.sleep(backoffTimeMs.toLong())
                    } catch (ex: InterruptedException) {
                        throw RuntimeException(ex)
                    }
                }
            }
            return null
        }
    }
}

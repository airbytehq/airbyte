/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import io.grpc.StatusRuntimeException;
import io.micronaut.context.annotation.Value;
import io.micronaut.core.util.StringUtils;
import io.temporal.api.workflowservice.v1.DescribeNamespaceRequest;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class TemporalInitializationUtils {

  @Inject
  private WorkflowServiceStubs temporalService;
  @Value("${temporal.cloud.namespace}")
  private String temporalCloudNamespace;

  /**
   * Blocks until the Temporal {@link TemporalUtils#DEFAULT_NAMESPACE} has been created. This is
   * necessary to avoid issues related to
   * https://community.temporal.io/t/running-into-an-issue-when-creating-namespace-programmatically/2783/8.
   */
  public void waitForTemporalNamespace() {
    boolean namespaceExists = false;
    final String temporalNamespace = getTemporalNamespace();
    while (!namespaceExists) {
      try {
        // This is to allow the configured namespace to be available in the Temporal
        // cache before continuing on with any additional configuration/bean creation.
        temporalService.blockingStub().describeNamespace(DescribeNamespaceRequest.newBuilder().setNamespace(temporalNamespace).build());
        namespaceExists = true;
        // This is to allow the configured namespace to be available in the Temporal
        // cache before continuing on with any additional configuration/bean creation.
        Thread.sleep(TimeUnit.SECONDS.toMillis(5));
      } catch (final InterruptedException | StatusRuntimeException e) {
        log.debug("Namespace '{}' does not exist yet.  Re-checking...", temporalNamespace);
        try {
          Thread.sleep(TimeUnit.SECONDS.toMillis(5));
        } catch (final InterruptedException ie) {
          log.debug("Sleep interrupted.  Exiting loop...");
        }
      }
    }
  }

  /**
   * Retrieve the Temporal namespace based on the configuration.
   *
   * @return The Temporal namespace.
   */
  private String getTemporalNamespace() {
    return StringUtils.isNotEmpty(temporalCloudNamespace) ? temporalCloudNamespace : TemporalUtils.DEFAULT_NAMESPACE;
  }

}

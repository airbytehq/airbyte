/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.aws_datalake;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.auth.credentials.AwsCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.athena.AthenaClient;
import software.amazon.awssdk.services.athena.model.AthenaException;
import software.amazon.awssdk.services.athena.model.GetQueryExecutionRequest;
import software.amazon.awssdk.services.athena.model.GetQueryExecutionResponse;
import software.amazon.awssdk.services.athena.model.GetQueryResultsRequest;
import software.amazon.awssdk.services.athena.model.QueryExecutionContext;
import software.amazon.awssdk.services.athena.model.QueryExecutionState;
import software.amazon.awssdk.services.athena.model.ResultConfiguration;
import software.amazon.awssdk.services.athena.model.StartQueryExecutionRequest;
import software.amazon.awssdk.services.athena.model.StartQueryExecutionResponse;
import software.amazon.awssdk.services.athena.paginators.GetQueryResultsIterable;

public class AthenaHelper {

  private AthenaClient athenaClient;
  private String outputBucket;
  private String workGroup;
  private static final Logger LOGGER = LoggerFactory.getLogger(AthenaHelper.class);

  public AthenaHelper(AwsCredentials credentials, Region region, String outputBucket, String workGroup) {
    LOGGER.debug(String.format("region = %s, outputBucket = %s, workGroup = %s", region, outputBucket, workGroup));
    var credProvider = StaticCredentialsProvider.create(credentials);
    this.athenaClient = AthenaClient.builder().region(region).credentialsProvider(credProvider).build();
    this.outputBucket = outputBucket;
    this.workGroup = workGroup;
  }

  public String submitAthenaQuery(String database, String query) {
    try {

      // The QueryExecutionContext allows us to set the database
      QueryExecutionContext queryExecutionContext = QueryExecutionContext.builder()
          .database(database).build();

      // The result configuration specifies where the results of the query should go
      ResultConfiguration resultConfiguration = ResultConfiguration.builder()
          .outputLocation(outputBucket)
          .build();

      StartQueryExecutionRequest startQueryExecutionRequest = StartQueryExecutionRequest.builder()
          .queryString(query)
          .queryExecutionContext(queryExecutionContext)
          .resultConfiguration(resultConfiguration)
          .workGroup(workGroup)
          .build();

      StartQueryExecutionResponse startQueryExecutionResponse = athenaClient.startQueryExecution(startQueryExecutionRequest);
      return startQueryExecutionResponse.queryExecutionId();
    } catch (AthenaException e) {
      e.printStackTrace();
      System.exit(1);
    }
    return "";
  }

  public void waitForQueryToComplete(String queryExecutionId) throws InterruptedException {
    GetQueryExecutionRequest getQueryExecutionRequest = GetQueryExecutionRequest.builder()
        .queryExecutionId(queryExecutionId).build();

    GetQueryExecutionResponse getQueryExecutionResponse;
    boolean isQueryStillRunning = true;
    while (isQueryStillRunning) {
      getQueryExecutionResponse = athenaClient.getQueryExecution(getQueryExecutionRequest);
      String queryState = getQueryExecutionResponse.queryExecution().status().state().toString();
      if (queryState.equals(QueryExecutionState.FAILED.toString())) {
        throw new RuntimeException("The Amazon Athena query failed to run with error message: " + getQueryExecutionResponse
            .queryExecution().status().stateChangeReason());
      } else if (queryState.equals(QueryExecutionState.CANCELLED.toString())) {
        throw new RuntimeException("The Amazon Athena query was cancelled.");
      } else if (queryState.equals(QueryExecutionState.SUCCEEDED.toString())) {
        isQueryStillRunning = false;
      } else {
        // Sleep an amount of time before retrying again
        Thread.sleep(1000);
      }
    }
  }

  public GetQueryResultsIterable getResults(String queryExecutionId) {

    try {

      // Max Results can be set but if its not set,
      // it will choose the maximum page size
      GetQueryResultsRequest getQueryResultsRequest = GetQueryResultsRequest.builder()
          .queryExecutionId(queryExecutionId)
          .build();

      GetQueryResultsIterable getQueryResultsResults = athenaClient.getQueryResultsPaginator(getQueryResultsRequest);
      return getQueryResultsResults;

    } catch (AthenaException e) {
      e.printStackTrace();
      System.exit(1);
    }
    return null;
  }

  public GetQueryResultsIterable runQuery(String database, String query) throws InterruptedException {
    int retryCount = 0;

    while (retryCount < 10) {
      var execId = submitAthenaQuery(database, query);
      try {
        waitForQueryToComplete(execId);
      } catch (RuntimeException e) {
        e.printStackTrace();
        LOGGER.info("Athena query failed once. Retrying.");
        retryCount++;
        continue;
      }
      return getResults(execId);
    }
    LOGGER.info("Athena query failed and we are out of retries.");
    return null;
  }

}

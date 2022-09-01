/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class SentryExceptionHelperTest {

  private static final String ERROR_PATH = "/airbyte/connector-errors/error.py";
  private static final String ABS_PATH = "abspath";
  private static final String LINE_NO = "lineno";
  private static final String FUNCTION = "function";
  private static final String CONTEXT_LINE = "context_line";
  private static final String FILENAME = "filename";
  private static final String MODULE = "module";

  final SentryExceptionHelper exceptionHelper = new SentryExceptionHelper();

  @Test
  void testBuildSentryExceptionsInvalid() {
    final String stacktrace = "this is not a stacktrace";
    final Optional<List<SentryException>> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(exceptionList.isEmpty());
  }

  @Test
  void testBuildSentryExceptionsPartiallyInvalid() {
    final String stacktrace = "Traceback (most recent call last):\n  Oops!";
    final Optional<List<SentryException>> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(exceptionList.isEmpty());
  }

  @Test
  void testBuildSentryExceptionsPythonChained() {
    final String stacktrace =
        """
        Traceback (most recent call last):
          File "/airbyte/connector-errors/error.py", line 31, in read_records
            failing_method()
          File "/airbyte/connector-errors/error.py", line 36, in failing_method
            raise HTTPError(http_error_msg, response=self)
        requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://airbyte.com

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "/airbyte/connector-errors/error.py", line 39, in <module>
            main()
          File "/airbyte/connector-errors/error.py", line 13, in main
            sync_mode("incremental")
          File "/airbyte/connector-errors/error.py", line 17, in sync_mode
            incremental()
          File "/airbyte/connector-errors/error.py", line 33, in incremental
            raise RuntimeError("My other error") from err
        RuntimeError: My other error
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(2, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "requests.exceptions.HTTPError", "400 Client Error: Bad Request for url: https://airbyte.com",
        List.of(
            Map.of(
                ABS_PATH, ERROR_PATH,
                LINE_NO, 31,
                FUNCTION, "read_records",
                CONTEXT_LINE, "failing_method()"),
            Map.of(
                ABS_PATH, ERROR_PATH,
                LINE_NO, 36,
                FUNCTION, "failing_method",
                CONTEXT_LINE, "raise HTTPError(http_error_msg, response=self)")));

    assertExceptionContent(exceptionList.get(1), "RuntimeError", "My other error", List.of(
        Map.of(
            ABS_PATH, ERROR_PATH,
            LINE_NO, 39,
            FUNCTION, "<module>",
            CONTEXT_LINE, "main()"),
        Map.of(
            ABS_PATH, ERROR_PATH,
            LINE_NO, 13,
            FUNCTION, "main",
            CONTEXT_LINE, "sync_mode(\"incremental\")"),
        Map.of(
            ABS_PATH, ERROR_PATH,
            LINE_NO, 17,
            FUNCTION, "sync_mode",
            CONTEXT_LINE, "incremental()"),
        Map.of(
            ABS_PATH, ERROR_PATH,
            LINE_NO, 33,
            FUNCTION, "incremental",
            CONTEXT_LINE, "raise RuntimeError(\"My other error\") from err")));

  }

  @Test
  void testBuildSentryExceptionsPythonNoValue() {
    final String stacktrace =
        """
        Traceback (most recent call last):
          File "/airbyte/connector-errors/error.py", line 33, in incremental
            raise RuntimeError()
        RuntimeError
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "RuntimeError", null, List.of(
        Map.of(
            ABS_PATH, ERROR_PATH,
            LINE_NO, 33,
            FUNCTION, "incremental",
            CONTEXT_LINE, "raise RuntimeError()")));
  }

  @Test
  void testBuildSentryExceptionsPythonMultilineValue() {
    final String stacktrace =
        """
        Traceback (most recent call last):
          File "/usr/local/lib/python3.9/site-packages/grpc/_channel.py", line 849, in _end_unary_response_blocking
            raise _InactiveRpcError(state)
        grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
          status = StatusCode.INTERNAL
          details = "Internal error encountered."
        >

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "/usr/local/lib/python3.9/site-packages/google/api_core/exceptions.py", line 553, in _parse_grpc_error_details
            status = rpc_status.from_call(rpc_exc)
        AttributeError: 'NoneType' object has no attribute 'from_call'
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(2, exceptionList.size());

    final String expectedValue =
        """
        <_InactiveRpcError of RPC that terminated with:
          status = StatusCode.INTERNAL
          details = "Internal error encountered."
        >""";

    assertExceptionContent(exceptionList.get(0), "grpc._channel._InactiveRpcError", expectedValue, List.of(
        Map.of(
            ABS_PATH, "/usr/local/lib/python3.9/site-packages/grpc/_channel.py",
            LINE_NO, 849,
            FUNCTION, "_end_unary_response_blocking",
            CONTEXT_LINE, "raise _InactiveRpcError(state)")));

    assertExceptionContent(exceptionList.get(1), "AttributeError", "'NoneType' object has no attribute 'from_call'", List.of(
        Map.of(
            ABS_PATH, "/usr/local/lib/python3.9/site-packages/google/api_core/exceptions.py",
            LINE_NO, 553,
            FUNCTION, "_parse_grpc_error_details",
            CONTEXT_LINE, "status = rpc_status.from_call(rpc_exc)")));
  }

  @Test
  void testBuildSentryExceptionsJava() {
    final String stacktrace =
        """
        java.lang.ArithmeticException: / by zero
        	at io.airbyte.integrations.base.AirbyteTraceMessageUtilityTest.testCorrectStacktraceFormat(AirbyteTraceMessageUtilityTest.java:61)
        	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        	at org.junit.jupiter.engine.execution.ExecutableInvoker$ReflectiveInterceptorCall.lambda$ofVoidMethod$0(ExecutableInvoker.java:115)
        	at app//org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
        	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
        	at jdk.proxy2/jdk.proxy2.$Proxy5.stop(Unknown Source)
        	at worker.org.gradle.process.internal.worker.GradleWorkerMain.main(GradleWorkerMain.java:74)
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "java.lang.ArithmeticException", "/ by zero",
        List.of(
            Map.of(
                FILENAME, "GradleWorkerMain.java",
                LINE_NO, 74,
                MODULE, "worker.org.gradle.process.internal.worker.GradleWorkerMain",
                FUNCTION, "main"),
            Map.of(
                MODULE, "jdk.proxy2.$Proxy5",
                FUNCTION, "stop"),
            Map.of(
                FILENAME, "ThrowableCollector.java",
                LINE_NO, 73,
                MODULE, "org.junit.platform.engine.support.hierarchical.ThrowableCollector",
                FUNCTION, "execute"),
            Map.of(
                FILENAME, "NodeTestTask.java",
                LINE_NO, 141,
                MODULE, "org.junit.platform.engine.support.hierarchical.NodeTestTask",
                FUNCTION, "lambda$executeRecursively$8"),
            Map.of(
                FILENAME, "ExecutableInvoker.java",
                LINE_NO, 115,
                MODULE, "org.junit.jupiter.engine.execution.ExecutableInvoker$ReflectiveInterceptorCall",
                FUNCTION, "lambda$ofVoidMethod$0"),
            Map.of(
                "isNative", true,
                MODULE, "jdk.internal.reflect.NativeMethodAccessorImpl",
                FUNCTION, "invoke0"),
            Map.of(
                FILENAME, "AirbyteTraceMessageUtilityTest.java",
                LINE_NO, 61,
                MODULE, "io.airbyte.integrations.base.AirbyteTraceMessageUtilityTest",
                FUNCTION, "testCorrectStacktraceFormat")));
  }

  @Test
  void testBuildSentryExceptionsJavaChained() {
    final String stacktrace =
        """
        java.util.concurrent.CompletionException: io.airbyte.workers.DefaultReplicationWorker$DestinationException: Destination process exited with non-zero exit code 1
        	at java.base/java.util.concurrent.CompletableFuture.encodeThrowable(CompletableFuture.java:315)
        	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635)
        	at java.base/java.lang.Thread.run(Thread.java:833)
        		Suppressed: io.airbyte.workers.exception.WorkerException: Source process exit with code 1. This warning is normal if the job was cancelled.
        				at io.airbyte.workers.internal.DefaultAirbyteSource.close(DefaultAirbyteSource.java:136)
        				at io.airbyte.workers.general.DefaultReplicationWorker.run(DefaultReplicationWorker.java:137)
        				at io.airbyte.workers.general.DefaultReplicationWorker.run(DefaultReplicationWorker.java:65)
        				at io.airbyte.workers.temporal.TemporalAttemptExecution.lambda$getWorkerThread$2(TemporalAttemptExecution.java:158)
        				at java.lang.Thread.run(Thread.java:833)
        Caused by: io.airbyte.workers.DefaultReplicationWorker$DestinationException: Destination process exited with non-zero exit code 1
        	at io.airbyte.workers.DefaultReplicationWorker.lambda$getDestinationOutputRunnable$7(DefaultReplicationWorker.java:397)
        	at java.base/java.util.concurrent.CompletableFuture$AsyncRun.run(CompletableFuture.java:1804)
        	... 3 more
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(2, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "java.util.concurrent.CompletionException",
        "io.airbyte.workers.DefaultReplicationWorker$DestinationException: Destination process exited with non-zero exit code 1",
        List.of(
            Map.of(
                FILENAME, "Thread.java",
                LINE_NO, 833,
                MODULE, "java.lang.Thread",
                FUNCTION, "run"),
            Map.of(
                FILENAME, "ThreadPoolExecutor.java",
                LINE_NO, 635,
                MODULE, "java.util.concurrent.ThreadPoolExecutor$Worker",
                FUNCTION, "run"),
            Map.of(
                FILENAME, "CompletableFuture.java",
                LINE_NO, 315,
                MODULE, "java.util.concurrent.CompletableFuture",
                FUNCTION, "encodeThrowable")));

    assertExceptionContent(exceptionList.get(1), "io.airbyte.workers.DefaultReplicationWorker$DestinationException",
        "Destination process exited with non-zero exit code 1", List.of(
            Map.of(
                FILENAME, "CompletableFuture.java",
                LINE_NO, 1804,
                MODULE, "java.util.concurrent.CompletableFuture$AsyncRun",
                FUNCTION, "run"),
            Map.of(
                FILENAME, "DefaultReplicationWorker.java",
                LINE_NO, 397,
                MODULE, "io.airbyte.workers.DefaultReplicationWorker",
                FUNCTION, "lambda$getDestinationOutputRunnable$7")));
  }

  @Test
  void testBuildSentryExceptionsJavaMultilineValue() {
    final String stacktrace =
        """
        io.temporal.failure.ApplicationFailure: GET https://storage.googleapis.com/
        {
          "code" : 401,
          "message" : "Invalid Credentials"
        }
        	at com.google.api.client.googleapis.json.GoogleJsonResponseException.from(GoogleJsonResponseException.java:146)
          ... 22 more
        Caused by: org.postgresql.util.PSQLException: ERROR: publication "airbyte_publication" does not exist
          Where: slot "airbyte_slot", output plugin "pgoutput", in the change callback, associated LSN 0/48029520
        	at org.postgresql.core.v3.QueryExecutorImpl.receiveErrorResponse(QueryExecutorImpl.java:2675)
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(2, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "io.temporal.failure.ApplicationFailure",
        """
        GET https://storage.googleapis.com/
        {
          "code" : 401,
          "message" : "Invalid Credentials"
        }""", List.of(
            Map.of(
                FILENAME, "GoogleJsonResponseException.java",
                LINE_NO, 146,
                MODULE, "com.google.api.client.googleapis.json.GoogleJsonResponseException",
                FUNCTION, "from")));

    assertExceptionContent(exceptionList.get(1), "org.postgresql.util.PSQLException",
        """
        ERROR: publication "airbyte_publication" does not exist
          Where: slot "airbyte_slot", output plugin "pgoutput", in the change callback, associated LSN 0/48029520""", List.of(
            Map.of(
                FILENAME, "QueryExecutorImpl.java",
                LINE_NO, 2675,
                MODULE, "org.postgresql.core.v3.QueryExecutorImpl",
                FUNCTION, "receiveErrorResponse")));
  }

  @Test
  void testBuildSentryExceptionsDbtDatabaseErrorDefault() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        1 of 1 ERROR creating table model public.midaug_start_users............................................................. [[31mERROR[0m in 0.24s]
        [33mDatabase Error in model midaug_start_users (models/generated/airbyte_incremental/public/midaug_start_users.sql)[0m
          1292 (22007): Truncated incorrect DOUBLE value: 'ABC'
          compiled SQL at ../build/run/airbyte_utils/models/generated/airbyte_incremental/public/midaug_start_users.sql
        1 of 1 ERROR creating table model public.midaug_start_users............................................................. [[31mERROR[0m in 0.24s]
        [33mDatabase Error in model midaug_start_users (models/generated/airbyte_incremental/public/midaug_start_users.sql)[0m
          1292 (22007): Truncated incorrect DOUBLE value: 'ABC'
          compiled SQL at ../build/run/airbyte_utils/models/generated/airbyte_incremental/public/midaug_start_users.sql
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtDatabaseError",
        "1292 (22007): Truncated incorrect DOUBLE value: 'ABC'", List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtDatabaseErrorSqlComp() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        4 of 14 ERROR creating incremental model RAW.GENERAL_LEDGER_TRANS....................................................... [[31mERROR[0m in 11.47s]
        	  [33mDatabase Error in model GENERAL_LEDGER_TRANS (models/generated/airbyte_incremental/RAW/GENERAL_LEDGER_TRANS.sql)[0m
        	  001003 (42000): SQL compilation error:
        	  syntax error line 47 at position 19 unexpected '-'.
        Setting attempt to FAILED because the job was cancelled
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtDatabaseSQLCompilationError",
        "001003 (42000): SQL compilation error: syntax error line 47 at position 19 unexpected '-'.", List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtDatabaseErrorInvalidInput() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        1 of 1 ERROR creating table model tdym_processing_test.tdym_api_data.................................................... [[31mERROR[0m in 0.61s]
        	  [33mDatabase Error in model tdym_api_data (models/generated/airbyte_tables/tdym_processing_test/tdym_api_data.sql)[0m
        	  Invalid input
        	  DETAIL:


        --	    error:  Invalid input
        	    code:      8001
        	    context:   SUPER value exceeds export size.
        	    query:     3667701
        	    location:  partiql_export.cpp:9
        	    process:   query0_127_3667701 [pid=17836]


        --	  compiled SQL at ../build/run/airbyte_utils/models/generated/airbyte_tables/tdym_processing_test/tdym_api_data.sql
        Setting attempt to FAILED because the job was cancelled
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtDatabaseInvalidInputError",
        "Invalid input\ncontext:   SUPER value exceeds export size.", List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtDatabaseErrorSyntax() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        1 of 3 ERROR creating incremental model _airbyte_public.products_stg.................................................... [[31mERROR[0m in 0.89s]
        	  [33mDatabase Error in model products_stg (models/generated/airbyte_incremental/public/products_stg.sql)[0m
            syntax error at or near "text"
        	  LINE 6:                add column Base name text
        	                                              ^
        	1 of 3 ERROR creating incremental model _airbyte_public.products_stg.................................................... [[31mERROR[0m in 0.89s]
        	  [33mDatabase Error in model products_stg (models/generated/airbyte_incremental/public/products_stg.sql)[0m
        	  syntax error at or near "text"
        	  LINE 6:                add column Base name text
        	                                              ^
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtDatabaseSyntaxError",
        "syntax error at or near \"text\"\nLINE 6:                add column Base name text", List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtUnhandledError() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
         [31mUnhandled error while executing model.airbyte_utils.1595965687212073_ads_insights_cost_per_2_sec_continuous_video_view_ab2[0m
        ("{'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}: None", {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}})
        	[31mUnhandled error while executing model.airbyte_utils.1595965687212073_ads_insights_video_avg_time_watched_actions_ab2[0m
        ("{'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}: None", {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}})
        	10 of 48 SKIP relation ba__facebook_ads.1595965687212073_ads_insights_cost_per_2_sec_continuous_video_view due to ephemeral model error [[31mERROR SKIP[0m]
        	[33m("{'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}: None", {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}})[0m
        	23 of 48 SKIP relation ba__facebook_ads.1595965687212073_ads_insights_video_avg_time_watched_actions due to ephemeral model error [[31mERROR SKIP[0m]
        	[33m("{'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}: None", {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}})[0m
        	[33mCompilation Error in model.airbyte_utils.1595965687212073_ads_insights_cost_per_2_sec_continuous_video_view, caused by compilation error in referenced ephemeral model model.airbyte_utils.1595965687212073_ads_insights_cost_per_2_sec_continuous_video_view_ab2[0m
        	[33mCompilation Error in model.airbyte_utils.1595965687212073_ads_insights_video_avg_time_watched_actions, caused by compilation error in referenced ephemeral model model.airbyte_utils.1595965687212073_ads_insights_video_avg_time_watched_actions_ab2[0m
        	[31mUnhandled error while executing model.airbyte_utils.1595965687212073_ads_insights_cost_per_2_sec_continuous_video_view_ab2[0m
        ("{'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}: None", {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}})
        	[33mCompilation Error in model.airbyte_utils.1595965687212073_ads_insights_video_avg_time_watched_actions, caused by compilation error in referenced ephemeral model model.airbyte_utils.1595965687212073_ads_insights_video_avg_time_watched_actions_ab2[0m
        	[33mCompilation Error in model.airbyte_utils.1595965687212073_ads_insights_video_p95_watched_actions, caused by compilation error in referenced ephemeral model model.airbyte_utils.1595965687212073_ads_insights_video_p95_watched_actions_ab2[0m
        	[33mCompilation Error in model.airbyte_utils.1595965687212073_ads_insights_video_time_watched_actions, caused by compilation error in referenced ephemeral model model.airbyte_utils.1595965687212073_ads_insights_video_time_watched_actions_ab2[0m
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtUnhandledError",
        "(\"{'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}: None\", {'error': {'code': 503, 'message': 'The service is currently unavailable.', 'status': 'UNAVAILABLE'}})",
        List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtCompilationErrorAmbigRelation() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        1 of 1 ERROR creating table model dbo.sheet1............................................................................ [[31mERROR[0m in 0.11s]
        	[33mCompilation Error in model sheet1 (models/generated/airbyte_tables/dbo/sheet1.sql)[0m
        	  When searching for a relation, dbt found an approximate match. Instead of guessing
        	  which relation to use, dbt will move on. Please delete "Data_integration"."dbo"."sheet1", or rename it to be less ambiguous.
        	  Searched for: "data_integration"."dbo"."sheet1"
        	  Found: "Data_integration"."dbo"."sheet1"

        	  > in macro materialization_table_default (macros/materializations/models/table/table.sql)
        	  > called by model sheet1 (models/generated/airbyte_tables/dbo/sheet1.sql)
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtCompilationAmbiguousRelationError",
        "When searching for a relation, dbt found an approximate match. Instead of guessing which relation to use, dbt will move on. Please delete \"Data_integration\".\"dbo\".\"sheet1\", or rename it to be less ambiguous.",
        List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtCompilationErrorDefault() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        Encountered an error:
        Compilation Error in model banking_test (models/generated/airbyte_tables/public/banking_test.sql)
          Model 'model.airbyte_utils.banking_test' (models/generated/airbyte_tables/public/banking_test.sql) depends on a source named 'public._airbyte_raw_banking_test' which was not found
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtCompilationError",
        "Model 'model.airbyte_utils.banking_test' (models/generated/airbyte_tables/public/banking_test.sql) depends on a source named 'public._airbyte_raw_banking_test' which was not found",
        List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtRuntimeErrorDefault() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        Encountered an error:
        Runtime Error
          Code: 102. Unexpected packet from server abcdefg.eu-west-1.aws.clickhouse.cloud:8443 (expected Hello or Exception, got Unknown packet)
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtRuntimeError",
        "Code: 102. Unexpected packet from server abcdefg.eu-west-1.aws.clickhouse.cloud:8443 (expected Hello or Exception, got Unknown packet)",
        List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtRuntimeErrorDatabase() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        Encountered an error:
        Runtime Error
          Database error while listing schemas in database ""AIRBYTE_DATABASE""
          Database Error
            250001 (08001): Failed to connect to DB: xyzxyz.us-east-2.aws.snowflakecomputing.com:443. The user you were trying to authenticate as differs from the user tied to the access token.
        message='io.temporal.serviceclient.CheckedExceptionWrapper: java.util.concurrent.ExecutionException: java.lang.RuntimeException: io.airbyte.workers.exception.WorkerException: Running the launcher replication-orchestrator failed', type='java.lang.RuntimeException', nonRetryable=false
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtRuntimeDatabaseError",
        "250001 (08001): Failed to connect to DB: xyzxyz.us-east-2.aws.snowflakecomputing.com:443. The user you were trying to authenticate as differs from the user tied to the access token.",
        List.of());
  }

  @Test
  void testBuildSentryExceptionsDbtDatabaseErrorOther() {
    final String stacktrace =
        """
        AirbyteDbtError:\s
        Encountered an error:
        Database Error
          Access Denied: Project upside-cloud-prod: User does not have bigquery.datasets.create permission in project upside-cloud-prod.
        Setting attempt to FAILED because the job was cancelled
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "DbtDatabaseError",
        "Access Denied: Project upside-cloud-prod: User does not have bigquery.datasets.create permission in project upside-cloud-prod.", List.of());
  }

  private void assertExceptionContent(final SentryException exception,
                                      final String type,
                                      final String value,
                                      final List<Map<String, Object>> frames) {
    Assertions.assertEquals(type, exception.getType());
    Assertions.assertEquals(value, exception.getValue());

    if (!frames.isEmpty()) {
      final SentryStackTrace stackTrace = exception.getStacktrace();
      Assertions.assertNotNull(stackTrace);
      final List<SentryStackFrame> sentryFrames = stackTrace.getFrames();
      Assertions.assertNotNull(sentryFrames);
      Assertions.assertEquals(frames.size(), sentryFrames.size());

      for (int i = 0; i < frames.size(); i++) {
        final Map<String, Object> expectedFrame = frames.get(i);
        final SentryStackFrame sentryFrame = sentryFrames.get(i);

        if (expectedFrame.containsKey(MODULE)) {
          Assertions.assertEquals(expectedFrame.get(MODULE), sentryFrame.getModule());
        }

        if (expectedFrame.containsKey(FILENAME)) {
          Assertions.assertEquals(expectedFrame.get(FILENAME), sentryFrame.getFilename());
        }

        if (expectedFrame.containsKey(ABS_PATH)) {
          Assertions.assertEquals(expectedFrame.get(ABS_PATH), sentryFrame.getAbsPath());
        }

        if (expectedFrame.containsKey(FUNCTION)) {
          Assertions.assertEquals(expectedFrame.get(FUNCTION), sentryFrame.getFunction());
        }

        if (expectedFrame.containsKey(LINE_NO)) {
          Assertions.assertEquals(expectedFrame.get(LINE_NO), sentryFrame.getLineno());
        }

        if (expectedFrame.containsKey(CONTEXT_LINE)) {
          Assertions.assertEquals(expectedFrame.get(CONTEXT_LINE), sentryFrame.getContextLine());
        }

        if (expectedFrame.containsKey("isNative")) {
          Assertions.assertEquals(expectedFrame.get("isNative"), sentryFrame.isNative());
        }
      }
    }
  }

}

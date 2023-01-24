/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server;

import io.airbyte.commons.io.IOs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import java.util.stream.Stream;
import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import lombok.RequiredArgsConstructor;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.slf4j.MDC;

@SuppressWarnings({"PMD.AvoidPrintStackTrace", "PMD.JUnitTestsShouldIncludeAssert"})
@ExtendWith(MockitoExtension.class)
class RequestLoggerTest {

  private static final String VALID_JSON_OBJECT = "{\"valid\":1}";
  private static final String INVALID_JSON_OBJECT = "invalid";
  private static final String ACCEPTED_CONTENT_TYPE = "application/json";
  private static final String NON_ACCEPTED_CONTENT_TYPE = "application/gzip";
  private static final String METHOD = "POST";
  private static final String REMOTE_ADDR = "123.456.789.101";
  private static final String URL = "/api/v1/test";
  private static final String REQUEST_BODY_PROPERTY = "requestBodyProperty";

  private static final Random RANDOM = new Random();

  @Mock
  private HttpServletRequest mServletRequest;

  private Path logPath;

  @BeforeEach
  void init() throws IOException {
    Mockito.when(mServletRequest.getMethod())
        .thenReturn(METHOD);
    Mockito.when(mServletRequest.getRemoteAddr())
        .thenReturn(REMOTE_ADDR);
    Mockito.when(mServletRequest.getRequestURI())
        .thenReturn(URL);

    // set up the mdc so that actually log to a file, so that we can verify that file logging captures
    // threads.
    final Path jobRoot = Files.createTempDirectory(Path.of("/tmp"), "mdc_test");
    LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.DOCKER,
        LogConfigs.EMPTY,
        jobRoot);
    logPath = jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
  }

  @Nested
  @DisplayName("Formats logs correctly")
  class RequestLoggerFormatsLogsCorrectly {

    private static final int ERROR_CODE = 401;
    private static final int SUCCESS_CODE = 200;
    private static final String errorPrefix = RequestLogger
        .createLogPrefix(REMOTE_ADDR, METHOD, ERROR_CODE, URL)
        .toString();
    private static final String successPrefix = RequestLogger
        .createLogPrefix(REMOTE_ADDR, METHOD, SUCCESS_CODE, URL)
        .toString();

    static Stream<Arguments> logScenarios() {
      return Stream.of(
          Arguments.of(INVALID_JSON_OBJECT, NON_ACCEPTED_CONTENT_TYPE, ERROR_CODE, errorPrefix),
          Arguments.of(INVALID_JSON_OBJECT, ACCEPTED_CONTENT_TYPE, ERROR_CODE, errorPrefix),
          Arguments.of(VALID_JSON_OBJECT, NON_ACCEPTED_CONTENT_TYPE, ERROR_CODE, errorPrefix),
          Arguments.of(VALID_JSON_OBJECT, ACCEPTED_CONTENT_TYPE, ERROR_CODE, errorPrefix + " - " + VALID_JSON_OBJECT),
          Arguments.of(INVALID_JSON_OBJECT, NON_ACCEPTED_CONTENT_TYPE, SUCCESS_CODE, successPrefix),
          Arguments.of(INVALID_JSON_OBJECT, ACCEPTED_CONTENT_TYPE, SUCCESS_CODE, successPrefix),
          Arguments.of(VALID_JSON_OBJECT, NON_ACCEPTED_CONTENT_TYPE, SUCCESS_CODE, successPrefix),
          Arguments.of(VALID_JSON_OBJECT, ACCEPTED_CONTENT_TYPE, SUCCESS_CODE, successPrefix + " - " + VALID_JSON_OBJECT));
    }

    @Mock
    private ContainerRequestContext mRequestContext;
    @Mock
    private ContainerResponseContext mResponseContext;

    private RequestLogger requestLogger;

    @ParameterizedTest
    @MethodSource("logScenarios")
    @DisplayName("Check that the proper log is produced based on the scenario")
    void test(final String requestBody, final String contentType, final int status, final String expectedLog) throws IOException {
      // We have to instanciate the logger here, because the MDC config has been changed to log in a
      // temporary file.
      requestLogger = new RequestLogger(MDC.getCopyOfContextMap(), mServletRequest);

      stubRequestContext(mRequestContext, requestBody);

      Mockito.when(mResponseContext.getStatus())
          .thenReturn(status);

      Mockito.when(mServletRequest.getHeader("Content-Type"))
          .thenReturn(contentType);

      // This is call to set the requestBody variable in the RequestLogger
      requestLogger.filter(mRequestContext);
      requestLogger.filter(mRequestContext, mResponseContext);

      final String expectedLogLevel = status == SUCCESS_CODE ? "INFO" : "ERROR";

      final String logs = IOs.readFile(logPath);
      final Stream<String> matchingLines = logs.lines()
          .filter(line -> line.endsWith(expectedLog))
          .filter(line -> line.contains(expectedLogLevel));

      Assertions.assertThat(matchingLines).hasSize(1);
    }

  }

  @Nested
  @DisplayName("Logs correct requestBody")
  class RequestLoggerCorrectRequestBody {

    /**
     * This is a complex test that was written to prove that our requestLogger had a concurrency bug
     * that caused incorrect request bodies to be logged. The RequestLogger originally used an instance
     * variable that held the requestBody, which was written to by the request filter, and read by the
     * response filter to generate a response log line that contained the original request body. If
     * multiple requests were being processed at the same time, it was possible for the request filter
     * of one request to overwrite the requestBody instance variable before the response log line was
     * generated. The fixed implementation sets the requestBody as a custom property on the
     * ContainerRequestFilter in the first filter method, and reads the custom requestBody property from
     * the ContainerRequestFilter in the second filter method.
     * <p>
     * To cover this race condition, this test creates a single RequestLogger instance that is
     * referenced from 100 threads. Each thread logs a unique request body. The main thread waits for
     * all threads to finish, and then assures that every unique request body is included in the logs.
     * <p>
     * This test fails when using the instance variable approach for recording request bodies, because
     * some request bodies are overwritten before they can be logged.
     */
    @Test
    void testRequestBodyConsistency() {
      Mockito.when(mServletRequest.getHeader("Content-Type"))
          .thenReturn(ACCEPTED_CONTENT_TYPE);

      final RequestLogger requestLogger = new RequestLogger(MDC.getCopyOfContextMap(), mServletRequest);

      final List<RequestResponseRunnable> testCases = new ArrayList<>();
      final List<Thread> threads = new ArrayList<>();

      for (int i = 1; i < 100; i++) {
        testCases.add(createRunnableTestCase(requestLogger, UUID.randomUUID()));
      }

      testCases.forEach(testCase -> {
        final Thread thread = new Thread(testCase);
        threads.add(thread);
        thread.start();
      });

      threads.forEach(thread -> {
        try {
          thread.join();
        } catch (final InterruptedException e) {
          e.printStackTrace();
        }
      });

      testCases.forEach(testCase -> Assertions.assertThat(testCase.requestBodyWasLogged()).isTrue());
    }

    private RequestResponseRunnable createRunnableTestCase(final RequestLogger requestLogger, final UUID threadIdentifier) {

      // create thread-specific context mocks
      final ContainerRequestContext mRequestContext = Mockito.mock(ContainerRequestContext.class);
      final ContainerResponseContext mResponseContext = Mockito.mock(ContainerResponseContext.class);

      final String expectedRequestBody = String.format("{\"threadIdentifier\":\"%s\"}", threadIdentifier);

      stubRequestContext(mRequestContext, expectedRequestBody);

      return new RequestResponseRunnable(requestLogger, expectedRequestBody, mRequestContext, mResponseContext);
    }

    @RequiredArgsConstructor
    class RequestResponseRunnable implements Runnable {

      private final RequestLogger requestLogger;
      private final String expectedRequestBody;
      private final ContainerRequestContext mRequestContext;
      private final ContainerResponseContext mResponseContext;

      @Override
      public void run() {
        try {
          requestLogger.filter(mRequestContext);
          Thread.sleep(RANDOM.nextInt(1000)); // random sleep to make race more likely
          requestLogger.filter(mRequestContext, mResponseContext);
        } catch (final IOException | InterruptedException e) {
          e.printStackTrace();
        }
      }

      // search all log lines to see if this thread's request body was logged
      Boolean requestBodyWasLogged() {
        return IOs.readFile(logPath).lines().anyMatch(line -> line.contains(expectedRequestBody));
      }

    }

  }

  private void stubRequestContext(final ContainerRequestContext mockContainerRequestContext, final String requestBody) {
    Mockito.when(mockContainerRequestContext.getMethod())
        .thenReturn(METHOD);

    Mockito.when(mockContainerRequestContext.getEntityStream())
        .thenReturn(new ByteArrayInputStream(requestBody.getBytes(StandardCharsets.UTF_8)));

    Mockito.when(mockContainerRequestContext.getProperty(REQUEST_BODY_PROPERTY)).thenReturn(requestBody);
  }

}

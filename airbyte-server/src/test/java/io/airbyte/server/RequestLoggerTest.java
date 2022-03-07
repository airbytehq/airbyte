/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.commons.io.IOs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.stream.Stream;
import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import lombok.RequiredArgsConstructor;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.slf4j.MDC;

@ExtendWith(MockitoExtension.class)
public class RequestLoggerTest {

  private static final String VALID_JSON_OBJECT = "{\"valid\":1}";
  private static final String INVALID_JSON_OBJECT = "invalid";
  private static final String ACCEPTED_CONTENT_TYPE = "application/json";
  private static final String NON_ACCEPTED_CONTENT_TYPE = "application/gzip";

  private static final String METHOD = "POST";
  private static final String REMOTE_ADDR = "123.456.789.101";
  private static final String URL = "/api/v1/test";

  @Mock
  private HttpServletRequest mServletRequest;

  @BeforeEach
  public void init() {
    Mockito.when(mServletRequest.getMethod())
        .thenReturn(METHOD);
    Mockito.when(mServletRequest.getRemoteAddr())
        .thenReturn(REMOTE_ADDR);
    Mockito.when(mServletRequest.getRequestURI())
        .thenReturn(URL);
  }

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

  @ParameterizedTest
  @MethodSource("logScenarios")
  @DisplayName("Check that the proper log is produced based on the scenario")
  public void test(final String inputByteBuffer, final String contentType, final int status, final String expectedLog) throws IOException {
    // set up the mdc so that actually log to a file, so that we can verify that file logging captures
    // threads.
    final Path jobRoot = Files.createTempDirectory(Path.of("/tmp"), "mdc_test");
    LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.DOCKER,
        LogConfigs.EMPTY,
        jobRoot);

    // We have to instanciate the logger here, because the MDC config has been changed to log in a
    // temporary file.
    final RequestLogger requestLogger = new RequestLogger(MDC.getCopyOfContextMap(), mServletRequest);

    final ContainerRequestContext mRequestContext = Mockito.mock(ContainerRequestContext.class);
    final ContainerResponseContext mResponseContext = Mockito.mock(ContainerResponseContext.class);

    Mockito.when(mRequestContext.getMethod())
        .thenReturn(METHOD);

    Mockito.when(mRequestContext.getEntityStream())
        .thenReturn(new ByteArrayInputStream(inputByteBuffer.getBytes()));
    Mockito.when(mResponseContext.getStatus())
        .thenReturn(status);
    Mockito.when(mServletRequest.getHeader("Content-Type"))
        .thenReturn(contentType);

    // This is call to set the requestBody variable in the RequestLogger
    requestLogger.filter(mRequestContext);
    requestLogger.filter(mRequestContext, mResponseContext);

    final String expectedLogLevel = status == SUCCESS_CODE ? "INFO" : "ERROR";

    final Path logPath = jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    final String logs = IOs.readFile(logPath);
    final Stream<String> matchingLines = logs.lines()
        .filter(line -> line.endsWith(expectedLog))
        .filter(line -> line.contains(expectedLogLevel));

    Assertions.assertThat(matchingLines).hasSize(1);
  }

  /**
   * This is a complex test that was written to prove that our requestLogger had a concurrency bug that caused incorrect request bodies to be logged.
   * The RequestLogger originally used an instance variable that held the requestBody, which was written to by the request filter, and read by the
   * response filter to generate a response log line that contained the original request body. If multiple requests were being processed at the same
   * time, it was possible for the request filter of one request to overwrite the requestBody instance variable before the response log line was
   * generated.
   * <p>
   * To cover this race condition, this test creates a single RequestLogger instance that is referenced from 100 threads. Each thread has a unique
   * expected request body, and calls the request/response filter methods to retrieve it from a mocked context. Each thread stores its expected
   * request body, and the actual request body that would be logged. The main thread then waits for all threads to finish, and then loops over each
   * runnable to see if the expected request body matched the actual request body.
   * <p>
   * This test fails when using the instance variable approach for recording request bodies, and passes when using MDC to store the request body
   * between the request filter and the response filter.
   */
  @Test
  public void testRequestBodyConsistency() {
    final RequestLogger requestLogger = new RequestLogger(MDC.getCopyOfContextMap(), mServletRequest);

    final List<RequestResponseRunnable> testCases = new ArrayList<>();
    final List<Thread> threads = new ArrayList<>();

    for (int i = 1; i < 100; i++) {
      testCases.add(createRunnableTestCase(requestLogger, "thread" + i));
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

    testCases.forEach(testCase -> Assertions.assertThat(testCase.hadExpectedRequestBody()).isTrue());
  }

  private RequestResponseRunnable createRunnableTestCase(final RequestLogger requestLogger, final String threadIdentifier) {
    final String expectedRequestBody = String.format("{\"thread\":\"%s\"}", threadIdentifier);

    // create thread-specific mocks
    final ContainerRequestContext mRequestContext = Mockito.mock(ContainerRequestContext.class);
    final ContainerResponseContext mResponseContext = Mockito.mock(ContainerResponseContext.class);

    Mockito.when(mRequestContext.getMethod())
        .thenReturn(METHOD);
    Mockito.when(mRequestContext.getEntityStream())
        .thenReturn(new ByteArrayInputStream(expectedRequestBody.getBytes()));

    return new RequestResponseRunnable(requestLogger, expectedRequestBody, mRequestContext, mResponseContext);
  }

  @RequiredArgsConstructor
  public class RequestResponseRunnable implements Runnable {

    private final RequestLogger requestLogger;
    private final String expectedRequestBody;
    private final ContainerRequestContext mRequestContext;
    private final ContainerResponseContext mResponseContext;

    String actualRequestBody;

    public void run() {
      try {
        requestLogger.filter(mRequestContext);
        Thread.sleep(new Random().nextInt(1000)); // random sleep to make race more likely
        requestLogger.filter(mRequestContext, mResponseContext);
      } catch (final IOException | InterruptedException e) {
        e.printStackTrace();
      }
      actualRequestBody = requestLogger.getRequestBody();
    }

    public Boolean hadExpectedRequestBody() {
      final Boolean result = expectedRequestBody.equals(actualRequestBody);
      if (!result) {
        System.out.println("unexpected result! expected " + expectedRequestBody + " but actual was " + actualRequestBody);
      }
      return result;
    }
  }
}


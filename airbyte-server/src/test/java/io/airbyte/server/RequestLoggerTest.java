/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.commons.io.IOs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfiguration;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
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

  @Mock
  private ContainerRequestContext mRequestContext;

  @Mock
  private ContainerResponseContext mResponseContext;

  private RequestLogger requestLogger;

  @BeforeEach
  public void init() throws Exception {
    Mockito.when(mRequestContext.getMethod())
        .thenReturn(METHOD);

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
        LogConfiguration.EMPTY,
        jobRoot);

    // We have to instanciate the logger here, because the MDC config has been changed to log in a
    // temporary file.
    requestLogger = new RequestLogger(MDC.getCopyOfContextMap(), mServletRequest);

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

}

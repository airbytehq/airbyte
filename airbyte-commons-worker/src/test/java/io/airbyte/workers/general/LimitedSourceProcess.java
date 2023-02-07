/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.lang.ProcessHandle.Info;
import java.nio.charset.Charset;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.Executors;

/**
 * Basic Airbyte Source that emits {@link LimitedSourceProcess#TOTAL_RECORDS} before finishing.
 * Intended for performance testing.
 */
public class LimitedSourceProcess extends Process {

  private static final int TOTAL_RECORDS = 2_000_000;
  private static final ObjectMapper MAPPER = new ObjectMapper();

  private int currRecs = 0;
  private final PipedInputStream is = new PipedInputStream();

  @Override
  public OutputStream getOutputStream() {
    return null;
  }

  @Override
  public InputStream getInputStream() {
    final OutputStream os;
    // start writing to the input stream
    try {
      os = new PipedOutputStream(is);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    Executors.newSingleThreadExecutor().submit(
        () -> {
          try {
            while (currRecs != TOTAL_RECORDS) {
              var msg = AirbyteMessageUtils.createRecordMessage("s1", "data",
                  "This is a fairly long sentence to provide some bytes here. More bytes is better as it helps us measure performance."
                      + "Random append to prevent dead code generation :");
              os.write(MAPPER.writeValueAsString(msg).getBytes(Charset.defaultCharset()));
              os.write(System.getProperty("line.separator").getBytes(Charset.defaultCharset()));
              currRecs++;
            }
            os.flush();
            os.close();
          } catch (IOException e) {
            throw new RuntimeException(e);
          }
        });

    return is;
  }

  @Override
  public InputStream getErrorStream() {
    return new PipedInputStream();
  }

  @Override
  public int waitFor() throws InterruptedException {
    while (exitValue() != 0) {
      Thread.sleep(1000 * 10);
    }
    return exitValue();
  }

  @Override
  public int exitValue() {
    if (currRecs == TOTAL_RECORDS) {
      try {
        is.close();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      return 0;
    }

    throw new IllegalThreadStateException("process hasn't exited");

  }

  @Override
  public void destroy() {
    currRecs = TOTAL_RECORDS;

    try {
      is.close();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public Info info() {
    return new TestProcessInfo();
  }

  static class TestProcessInfo implements Info {

    @Override
    public Optional<String> command() {
      return Optional.of("test process");
    }

    @Override
    public Optional<String> commandLine() {
      return Optional.of("test process");
    }

    @Override
    public Optional<String[]> arguments() {
      return Optional.empty();
    }

    @Override
    public Optional<Instant> startInstant() {
      return Optional.empty();
    }

    @Override
    public Optional<Duration> totalCpuDuration() {
      return Optional.empty();
    }

    @Override
    public Optional<String> user() {
      return Optional.empty();
    }

  }

  public static void main(String[] args) {}

}

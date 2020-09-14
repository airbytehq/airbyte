package io.dataline.workers.protocols.singer;

import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.InvalidCredentialsException;
import java.io.Closeable;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.Optional;

public interface SingerTap extends AutoCloseable {

  void start(StandardTapConfig input, Path jobRoot) throws IOException, InvalidCredentialsException;

  boolean isFinished();

  Optional<SingerMessage> attemptRead();

  @Override
  void close() throws Exception;
}

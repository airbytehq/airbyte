package io.dataline.workers.protocols.singer;

import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.InvalidCredentialsException;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Iterator;

public interface SingerTap extends Iterator<SingerMessage> {

  void start(StandardTapConfig input, Path jobRoot) throws IOException, InvalidCredentialsException;

  @Override
  boolean hasNext();

  @Override
  SingerMessage next();

  void stop() throws IOException;
}

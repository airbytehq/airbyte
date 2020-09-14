package io.dataline.workers.protocols.singer;

import io.dataline.commons.functional.CheckedConsumer;
import io.dataline.config.StandardTargetConfig;
import io.dataline.singer.SingerMessage;
import java.io.Closeable;
import java.io.IOException;
import java.nio.file.Path;

public interface SingerTarget extends CheckedConsumer<SingerMessage, IOException>, Closeable {

  void start(StandardTargetConfig targetConfig, Path jobRoot);

  @Override
  void accept(SingerMessage message) throws IOException;

  void notifyEndOfStream() throws IOException;

  @Override
  void close();
}

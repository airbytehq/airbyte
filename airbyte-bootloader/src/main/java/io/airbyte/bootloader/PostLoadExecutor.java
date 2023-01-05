package io.airbyte.bootloader;

public interface PostLoadExecutor {

  void execute() throws Exception;
}

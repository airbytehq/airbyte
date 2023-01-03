/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.run;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.JobOutput;
import io.airbyte.workers.OutputAndStatus;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WorkerRunTest {

  private Path path;

  @BeforeEach
  void setUp() throws IOException {
    path = Files.createTempDirectory("test").resolve("sub").resolve("sub");
  }

  @SuppressWarnings("unchecked")
  @Test
  void test() throws Exception {
    final CheckedSupplier<OutputAndStatus<JobOutput>, Exception> supplier = mock(CheckedSupplier.class);
    new WorkerRun(path, supplier, "unknown airbyte version").call();

    assertTrue(Files.exists(path));
    verify(supplier).get();
  }

}

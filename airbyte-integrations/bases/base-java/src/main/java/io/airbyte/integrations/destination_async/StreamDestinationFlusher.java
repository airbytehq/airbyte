/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.stream.Stream;

/**
 * An interface meant to be used with {@link UploadWorkers}.
 * <p>
 * A destination instructs workers how to write data by specifying flush. This keeps the worker
 * abstraction generic and reusable.
 * <p>
 * e.g. A database destination's flush function likely involves parsing the stream into SQL
 * statements.
 * <p>
 * There are 2 different destination types as of this writing:
 * <ul>
 * <li>1. Destinations that upload files. This covers includes warehouses and databases.</li>
 * <li>1. Destinations that upload data streams. This mostly includes various Cloud storages.</li>
 * </ul>
 * In both cases, the incoming data can be modeled as a stream.
 */
public interface StreamDestinationFlusher {

  /**
   * @param decs the Airbyte stream the data stream belongs to
   * @param stream a bounded {@link AirbyteMessage} stream ideally of
   *        {@link #getOptimalBatchSizeBytes()} size
   * @throws Exception
   */
  void flush(StreamDescriptor decs, Stream<AirbyteMessage> stream) throws Exception;

  /**
   * When invoking {@link #flush(StreamDescriptor, Stream)}, best effort attempt to invoke flush with
   * a batch of this size. Useful for Destinations that have optimal flush batch sizes.
   *
   * @return the optimal batch size in bytes
   */
  long getOptimalBatchSizeBytes();

}

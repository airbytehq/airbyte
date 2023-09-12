package io.airbyte.integrations.destination.snowflake.demo.file_based.platform;

import static java.util.stream.Collectors.toMap;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestinationFactory;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.DataWriter;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.StorageLocation;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer.RecordRenderer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Supplier;

public class PlatformStuff<T extends StorageLocation> {

  private final ParsedCatalog catalog;
  private final JsonNode config;
  private final StreamDestinationFactory<? super T> streamDestinationFactory;
  private final RecordRenderer recordRenderer;
  private final Supplier<DataWriter<? extends T>> recordWriterFactory;
  private final int targetByteSizePerFile;

  // There are probably a ton more parameters here. In reality we would make this a builder.
  public PlatformStuff(final ConfiguredAirbyteCatalog inputCatalog,
                       final JsonNode config,
                       final StreamDestinationFactory<? super T> streamDestinationFactory,
                       final RecordRenderer recordRenderer,
                       final Supplier<DataWriter<? extends T>> recordWriterFactory,
                       final int targetByteSizePerFile) {
    this.recordRenderer = recordRenderer;
    this.recordWriterFactory = recordWriterFactory;
    // TODO: remove the sqlgenerator argument from this constructor
    final CatalogParser parser = new CatalogParser(null);

    this.catalog = parser.parseCatalog(inputCatalog);
    this.config = config;
    this.streamDestinationFactory = streamDestinationFactory;
    this.targetByteSizePerFile = targetByteSizePerFile;
  }

  public void doTheSyncThing() throws Exception {
    // maybe we should just pass config into the factory constructor...
    streamDestinationFactory.setup(config);

    // Parallel maps :( the StreamDestination and RecordWriter should probably be bundled together under a single class.
    // I'm guessing the existing async framework already does something like this.
    final Map<StreamId, StreamDestination<? super T>> streamDestinations = catalog.streams().stream()
        .collect(toMap(
            StreamConfig::id,
            streamDestinationFactory::build
        ));
    final Map<StreamId, DataWriter<? extends T>> streamWriters = catalog.streams().stream()
        .collect(toMap(
            StreamConfig::id,
            stream -> recordWriterFactory.get()
        ));

    // do these setups in parallel.
    for (final StreamDestination<? super T> streamDestination : streamDestinations.values()) {
      streamDestination.setup();
    }

    // while we have messages on stdin, process those messages
    // This basically represents AsyncFlush, I just wanted to demo how it hooks into the destinations code.
    while (true) {
      // Read a thing from stdin
      final AirbyteMessage message = null;

      switch (message.getType()) {
        case RECORD -> {
          // Write record to file, track memory, etc.
          final byte[] data = recordRenderer.render(message.getRecord());
          final DataWriter<? extends T> writer = streamWriters.get(message.getRecord().getStream());
          writer.getCurrentOutputStream().accept(data);
          // track the total size of data in bytes, record count, etc.

          // whenever we finish a file (either by reaching the target size, or by hitting a 15-minute deadline)
          // push it into the destination code
          final boolean fileReadyToUpload = false;
          if (fileReadyToUpload) {
            final StreamDestination<? super T> streamDestination = streamDestinations.get(message.getRecord().getStream());
            streamDestination.upload(writer.getCurrentLocation(), 42, 42);
            // emit state messages
            // update last commit time = now()
          }
        }
        case STATE -> {
          // do the state stuff
        }
      }
    }

    // Close all the stream destinations.
    // In reality, these should be done in parallel.
    for (final StreamDestination streamDestination : streamDestinations.values()) {
      streamDestination.close();
    }

    // Close any shared resources
    streamDestinationFactory.close();
  }
}

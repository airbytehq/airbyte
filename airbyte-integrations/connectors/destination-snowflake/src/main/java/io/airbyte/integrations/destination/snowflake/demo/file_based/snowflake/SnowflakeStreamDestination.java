package io.airbyte.integrations.destination.snowflake.demo.file_based.snowflake;

import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.snowflake.demo.file_based.iface.StreamDestination;
import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer.LocalFileDataWriter;

public class SnowflakeStreamDestination implements StreamDestination<LocalFileDataWriter.LocalFileLocation> {

  private final String originalStreamName;
  private final String originalStreamNamespace;
  private final String rawTableSchema;
  private final String rawTableName;
  private final String finalTableSchema;
  private final String finalTableName;
  private final String stageName;
  private final StreamConfig streamConfig;

  private final TypeAndDedupeOperationValve tdValve;
  private final TyperDeduper typerDeduper;

  public SnowflakeStreamDestination(final StreamConfig stream, final TypeAndDedupeOperationValve tdValve, final TyperDeduper typerDeduper) {
    this.originalStreamNamespace = stream.id().originalNamespace();
    this.originalStreamName = stream.id().originalName();
    this.rawTableName = originalStreamNamespace + "_raw__stream_" + originalStreamName;
    // generate the other table/schema names, etc.

    // also grab the T+D stuff. These are currently implemented for many-streams,
    // so we would need to swap them to be single-stream objects.
    this.tdValve = tdValve;
    this.typerDeduper = typerDeduper;
  }

  @Override
  public void setup() throws Exception {
    // CREATE STAGE <stage>
    // CREATE TABLE airbyte_internal.<rawTableName>

    // T+D setup (create final table, etc.)
    typerDeduper.prepareTables();
  }

  @Override
  public void upload(final LocalFileDataWriter.LocalFileLocation storage, final int numRecords, final int numBytes) throws Exception {
    // Snowflake's T+D code isn't safe to run concurrently with COPY INTO. Lock out other threads.
    typerDeduper.getRawTableWriteLock().lock();
    try {
      // TODO snowflake-jdbc opens a gcs/s3 upload object when running the PUT query - how can we track that memory usage?
      // PUT file:///.... INTO STAGE <stage>
      // COPY INTO <table> FROM STAGE <stage>
    } finally {
      typerDeduper.getRawTableWriteLock().lock();
    }

    if (tdValve.readyToTypeAndDedupe()) {
      // typeAndDedupe is threadsafe, so we don't need to explicity lock here.
      typerDeduper.typeAndDedupe(originalStreamNamespace, originalStreamName);
    }
  }

  @Override
  public void close() throws Exception {
    // PUT file:///.... INTO STAGE <stage>
    // COPY INTO <table> FROM STAGE <stage>
    // DROP STAGE <stage>

    typerDeduper.typeAndDedupe(originalStreamNamespace, originalStreamName);
  }
}

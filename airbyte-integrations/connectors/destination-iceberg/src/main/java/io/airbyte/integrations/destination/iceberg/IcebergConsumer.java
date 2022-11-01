package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static org.apache.logging.log4j.util.Strings.isNotBlank;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.iceberg.config.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.WriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.UUID;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.catalyst.expressions.GenericRow;
import org.apache.spark.sql.types.StringType$;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.types.TimestampType$;

/**
 * @author Leibniz on 2022/10/26.
 */
@Slf4j
public class IcebergConsumer extends CommitOnStateAirbyteMessageConsumer {

    private final NamingConventionTransformer namingResolver = new StandardNameTransformer();
    private final SparkSession spark;
    private final ConfiguredAirbyteCatalog catalog;
    private final IcebergCatalogConfig catalogConfig;

    private Map<AirbyteStreamNameNamespacePair, WriteConfig> writeConfigs;

    private final StructType normalizationSchema;

    public IcebergConsumer(SparkSession spark,
        Consumer<AirbyteMessage> outputRecordCollector,
        ConfiguredAirbyteCatalog catalog,
        IcebergCatalogConfig catalogConfig) {
        super(outputRecordCollector);
        this.spark = spark;
        this.catalog = catalog;
        this.catalogConfig = catalogConfig;
        this.normalizationSchema = new StructType().add(COLUMN_NAME_AB_ID, StringType$.MODULE$)
            .add(COLUMN_NAME_EMITTED_AT, TimestampType$.MODULE$)
            .add(COLUMN_NAME_DATA, StringType$.MODULE$);
    }

    /**
     * call this method to initialize any resources that need to be created BEFORE the consumer consumes any messages
     */
    @Override
    protected void startTracked() throws Exception {
        Map<AirbyteStreamNameNamespacePair, WriteConfig> configs = new HashMap<>();
//        String tempTablePrefix = Strings.addRandomSuffix("_airbyte_tmp", "_", 3) + "_";
        for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
            final String streamName = stream.getStream().getName().toLowerCase();
            String namespace = (isNotBlank(stream.getStream().getNamespace()) ?
                stream.getStream().getNamespace() :
                catalogConfig.getDefaultDatabase()
            ).toLowerCase();
            final String tableName = genTableName(namespace, "airbyte_raw_" + streamName);
            final String tmpTableName = genTableName(namespace, "_airbyte_tmp_" + streamName);
            final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
            if (syncMode == null) {
                throw new IllegalStateException("Undefined destination sync mode");
            }
            final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
            AirbyteStreamNameNamespacePair nameNamespacePair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream.getStream());
            configs.put(nameNamespacePair, new WriteConfig(tableName, tmpTableName, isAppendMode));
            try {
                spark.sql("DROP TABLE IF EXISTS " + tmpTableName);
            } catch (Exception e) {
                log.warn("Drop existed temp table failed: {}", e.getMessage(), e);
            }
        }
        this.writeConfigs = configs;
    }

    /**
     * call this method when receive a non-STATE AirbyteMessage Ref to <a
     * href="https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#airbytemessage">AirbyteMessage</a>
     */
    @Override
    protected void acceptTracked(AirbyteMessage msg) throws Exception {
        if (msg.getType() != Type.RECORD) {
            return;
        }
        final AirbyteRecordMessage recordMessage = msg.getRecord();

        // ignore other message types.
        AirbyteStreamNameNamespacePair nameNamespacePair = AirbyteStreamNameNamespacePair.fromRecordMessage(
            recordMessage);
        WriteConfig writeConfig = writeConfigs.get(nameNamespacePair);
        if (writeConfig == null) {
            throw new IllegalArgumentException(String.format(
                "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog),
                Jsons.serialize(recordMessage)));
        }

        // write data
        Row row = new GenericRow(new Object[]{
            UUID.randomUUID().toString(),
            new Timestamp(recordMessage.getEmittedAt()),
            Jsons.serialize(recordMessage.getData())
        });
        boolean needInsert = writeConfig.addData(row);
        if (needInsert) {
            appendToTempTable(writeConfig);
        }
    }

    private void appendToTempTable(WriteConfig writeConfig) {
        String tableName = writeConfig.getTmpTableName();
        List<Row> rows = writeConfig.fetchDataCache();
        //saveAsTable even if rows is empty, to ensure table is created.
        // otherwise the table would be missing, and throws exception in close()
        log.info("=> Flushing {} rows into {}", rows.size(), tableName);
        spark.createDataFrame(rows, normalizationSchema).write()
            // append data to temp table
            .mode(SaveMode.Append)
            // TODO make format as config
            .option("write-format", "parquet")
            .saveAsTable(tableName);
    }

    private String genTableName(String database, String tmpTableName) {
        return "%s.`%s`.`%s`".formatted(
            IcebergConstants.CATALOG_NAME,
            namingResolver.convertStreamName(database),
            namingResolver.convertStreamName(tmpTableName)
        );
    }

    /**
     * call this method when receive a STATE AirbyteMessage ———— it is the last message
     */
    @Override
    public void commit() throws Exception {
//        for (WriteConfig writeConfig : writeConfigs.values()) {
//            appendToTempTable(writeConfig);
//        }
    }

    @Override
    protected void close(boolean hasFailed) throws Exception {
        log.info("close {}, hasFailed={}", this.getClass().getSimpleName(), hasFailed);
        try {
            if (!hasFailed) {
                log.info("==> Migration finished with no explicit errors. Copying data from temp tables to permanent");
                for (WriteConfig writeConfig : writeConfigs.values()) {
                    appendToTempTable(writeConfig);
                    String tempTableName = writeConfig.getTmpTableName();
                    String finalTableName = writeConfig.getTableName();
                    log.info("=> Migration({}) data from {} to {}",
                        writeConfig.isAppendMode() ? "append" : "overwrite",
                        tempTableName,
                        finalTableName);
//                    if (writeConfig.isAppendMode()) {
                    spark.sql("SELECT * FROM %s".formatted(tempTableName))
//                            .coalesce(1)
                        .write()
                        .mode(writeConfig.isAppendMode() ? SaveMode.Append : SaveMode.Overwrite)
                        .saveAsTable(finalTableName);
//                    } else {
//                        spark.sql("DROP TABLE IF EXISTS %s".formatted(finalTableName));
//                        spark.sql("ALTER TABLE %s RENAME TO %s".formatted(tempTableName, finalTableName));
//                    }
                }
                log.info("==> Copy temp tables finished...");
            } else {
                log.error("Had errors while migrations");
            }
        } finally {
            log.info("Removing temp tables...");
            for (Entry<AirbyteStreamNameNamespacePair, WriteConfig> entry : writeConfigs.entrySet()) {
                try {
                    spark.sql("DROP TABLE IF EXISTS " + entry.getValue().getTmpTableName());
                } catch (Exception e) {
                    String errMsg = e.getMessage();
                    if (errMsg != null && errMsg.contains("Table or view not found")) {
                        log.warn("Drop temp table caught exception:{}", errMsg);
                    } else {
                        log.error("Drop temp table caught exception:{}", errMsg, e);
                    }
                }
            }
            log.info("Closing Spark Session...");
            this.spark.close();
            log.info("Finishing destination process...completed");
        }
    }
}

/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.time.Instant;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TypeAndDedupeTransaction {

  public static final String SOFT_RESET_SUFFIX = "_ab_soft_reset";
  private static final Logger LOGGER = LoggerFactory.getLogger(TypeAndDedupeTransaction.class);

  /**
   * It can be expensive to build the errors array in the airbyte_meta column, so we first attempt an
   * 'unsafe' transaction which assumes everything is typed correctly. If that fails, we will run a
   * more expensive query which handles casting errors
   *
   * @param sqlGenerator for generating sql for the destination
   * @param destinationHandler for executing sql created
   * @param streamConfig which stream to operate on
   * @param minExtractedAt to reduce the amount of data in the query
   * @param suffix table suffix for temporary tables
   * @throws Exception if the safe query fails
   */
  public static void executeTypeAndDedupe(final SqlGenerator sqlGenerator,
                                          final DestinationHandler destinationHandler,
                                          StreamConfig streamConfig,
                                          Optional<Instant> minExtractedAt,
                                          String suffix)
      throws Exception {
    try {
      LOGGER.info("Attempting typing and deduping for {}.{} with suffix", streamConfig.id().originalNamespace(), streamConfig.id().originalName(),
          suffix);
      final String unsafeSql = sqlGenerator.updateTable(streamConfig, suffix, minExtractedAt, false);
      destinationHandler.execute(unsafeSql);
      // TODO determine which Exceptions should not be retried even with safer sql
    } catch (Exception e) {
      LOGGER.error("Encountered Exception on unsafe SQL for stream {} {} with suffix {}, attempting with error handling",
          streamConfig.id().originalNamespace(), streamConfig.id().originalName(), suffix, e);
      final String saferSql = sqlGenerator.updateTable(streamConfig, suffix, minExtractedAt, true);
      destinationHandler.execute(saferSql);
    }
  }

  /**
   * Everything in
   * {@link TypeAndDedupeTransaction#executeTypeAndDedupe(SqlGenerator, DestinationHandler, StreamConfig, Optional, String)}
   * but with a little extra prep work for the soft reset temp tables
   *
   * @param sqlGenerator for generating sql for the destination
   * @param destinationHandler for executing sql created
   * @param streamConfig which stream to operate on
   * @throws Exception if the safe query fails
   */
  public static void executeSoftReset(final SqlGenerator sqlGenerator, final DestinationHandler destinationHandler, StreamConfig streamConfig)
      throws Exception {
    LOGGER.info("Attempting soft reset for stream {} {}", streamConfig.id().originalNamespace(), streamConfig.id().originalName());
    destinationHandler.execute(sqlGenerator.prepareTablesForSoftReset(streamConfig));
    executeTypeAndDedupe(sqlGenerator, destinationHandler, streamConfig, Optional.empty(), SOFT_RESET_SUFFIX);
    destinationHandler.execute(sqlGenerator.overwriteFinalTable(streamConfig.id(), SOFT_RESET_SUFFIX));
  }

}

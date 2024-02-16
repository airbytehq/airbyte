package io.airbyte.integrations.base.destination.typing_deduping;

import java.time.Instant;
import java.util.Optional;

public record InitialRawTableState(boolean hasUnprocessedRecords, Optional<Instant> maxProcessedTimestamp) {

}

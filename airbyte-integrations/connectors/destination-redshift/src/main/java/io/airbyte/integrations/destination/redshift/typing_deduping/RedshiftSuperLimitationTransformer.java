/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SizeBasedDataTransformer;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import kotlin.Pair;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.jetbrains.annotations.NotNull;

@Slf4j
public class RedshiftSuperLimitationTransformer extends SizeBasedDataTransformer {
  public static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;
  public static final int REDSHIFT_SUPER_MAX_BYTE_SIZE = 16 * 1024 * 1024;
  public RedshiftSuperLimitationTransformer(final ParsedCatalog parsedCatalog, final String defaultNamespace) {
    super(parsedCatalog, defaultNamespace, REDSHIFT_VARCHAR_MAX_BYTE_SIZE, REDSHIFT_SUPER_MAX_BYTE_SIZE);
  }


}

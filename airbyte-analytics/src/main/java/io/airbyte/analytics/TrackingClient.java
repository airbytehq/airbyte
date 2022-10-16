/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import java.util.Map;
import java.util.UUID;
import javax.annotation.Nullable;

/**
 * General interface for user level Airbyte usage reporting. We use Segment for behavioural
 * reporting, so this interface mirrors the Segment backend api sdk.
 * <p>
 * For more information see
 * https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/.
 * <p>
 * This interface allows us to easily stub this out via the {@link LoggingTrackingClient}. The main
 * implementation is in {@link SegmentTrackingClient}.
 * <p>
 * Although the methods seem to take in workspace id, this id is used to index into more metadata.
 * See {@link SegmentTrackingClient} for more information.
 * <p>
 * Keep in mind that this interface is also relied on in Airbyte Cloud.
 */
public interface TrackingClient {

  void identify(UUID workspaceId);

  void alias(UUID workspaceId, String previousCustomerId);

  void track(@Nullable UUID workspaceId, String action);

  void track(@Nullable UUID workspaceId, String action, Map<String, Object> metadata);

}

import { useEffect } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

import {
  DestinationDefinitionRead,
  DestinationRead,
  SourceDefinitionRead,
  SourceRead,
} from "core/request/AirbyteClient";
import { useGetDestination } from "hooks/services/useDestinationHook";
import { useGetSource } from "hooks/services/useSourceHook";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

export function hasSourceId(state: unknown): state is { sourceId: string } {
  return typeof state === "object" && state !== null && typeof (state as { sourceId?: string }).sourceId === "string";
}

export function hasDestinationId(state: unknown): state is { destinationId: string } {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { destinationId?: string }).destinationId === "string"
  );
}

export function usePreloadData(): {
  sourceDefinition?: SourceDefinitionRead;
  destination?: DestinationRead;
  source?: SourceRead;
  destinationDefinition?: DestinationDefinitionRead;
} {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const sourceIdFromLocationState = hasSourceId(location.state) && location.state.sourceId;
  const sourceIdFromSearchParams = searchParams.get("sourceId");
  const sourceId = sourceIdFromLocationState || sourceIdFromSearchParams;

  /**
   * There are two places we may find a sourceId, depending on the scenario. This effect
   * keeps them in sync according to the following logic:
   *   0) if `location.state.sourceId` and the `sourceId` query param are both unset or
   *      are both set to the same value, then we don't need to take any action.
   *   1) else if `location.state.sourceId` exists, we arrived at this page via the legacy
   *      internal "routing" system, meaning there has been a user interaction
   *      specifically selecting that source. This is the highest precedence source of
   *      truth, so if it exists we explicitly set the sourceId query param to match it.
   *   2) else if there's a `sourceId` query param, we arrived at this page via a fresh
   *      page load. This logic was added to support the airbyte-cloud's free connector
   *      program enrollment flow: it involves a round-trip visit to a Stripe domain,
   *      which wipes location.state. We explicitly navigate to the current path
   *      (including the current query string) with `location.state.sourceId` set.
   */
  useEffect(() => {
    if (sourceIdFromLocationState && sourceIdFromSearchParams === sourceIdFromLocationState) {
      // sourceId is set and everything is in sync, no further action needed
    } else if (sourceIdFromLocationState) {
      sourceId && setSearchParams({ sourceId });
    } else if (sourceIdFromSearchParams) {
      // we have to simultaneously set both the query string and location.state to avoid
      // an infinite mutually recursive rerender loop:
      //   A: set location.state and rerender; GOTO B
      //   B: set query param and rerender; GOTO A
      navigate(`${location.search}`, { state: { sourceId }, replace: true });
    } else {
      // sourceId is unset and everything is in sync, no further action needed
    }
  }, [sourceIdFromLocationState, sourceIdFromSearchParams, setSearchParams, navigate, sourceId, location.search]);
  const source = useGetSource(sourceId);

  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const destination = useGetDestination(hasDestinationId(location.state) ? location.state.destinationId : null);
  const destinationDefinition = useDestinationDefinition(destination?.destinationDefinitionId);

  return { source, sourceDefinition, destination, destinationDefinition };
}

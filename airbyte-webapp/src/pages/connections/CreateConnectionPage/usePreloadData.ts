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

  const destinationIdFromLocationState = hasDestinationId(location.state) && location.state.destinationId;
  const destinationIdFromSearchParams = searchParams.get("destinationId");
  const destinationId = destinationIdFromLocationState || destinationIdFromSearchParams;

  /**
   * There are two places we may find a sourceId or destinationId, depending on the
   * scenario. This effect keeps each of them in sync according to the following logic;
   * sourceId and destinationId sort out their sources of truth by parallel logic, so I'll
   * use `connectorId` as a generic stand-in:
   *   0) if `location.state.connectorId` and the `connectorId` query param are both unset or
   *      are both set to the same value, then we don't need to take any action.
   *   1) else if `location.state.connectorId` exists, we arrived at this page via the legacy
   *      internal "routing" system, meaning there has been a user interaction
   *      specifically selecting that source/destination. This is the highest precedence
   *      source of truth, so if it exists we just want to make the `connectorId` query
   *      param match it.
   *   2) else if there's a `connectorId` query param, we arrived at this page via a fresh
   *      page load. This logic was added to support the airbyte-cloud's free connector
   *      program enrollment flow (which involves a round-trip visit to a Stripe domain,
   *      which wipes location.state), but it's not explicitly tied to it. We explicitly
   *      navigate to the current path (including the current query string, to avoid going
   *      around in circles) while setting the missing `location.state.connectorId`.
   *
   * There are several states for each kind of connector, so let's extract a bunch of named
   * boolean variables to try to keep the combinations readable.
   */
  const sourceIdInBoth = sourceIdFromLocationState && sourceIdFromSearchParams === sourceIdFromLocationState;
  const sourceIdInNeither = !sourceIdFromLocationState && !sourceIdFromSearchParams;
  const sourceIdInSync = sourceIdInBoth || sourceIdInNeither;

  const destinationIdInBoth =
    destinationIdFromLocationState && destinationIdFromSearchParams === destinationIdFromLocationState;
  const destinationIdInNeither = !destinationIdFromLocationState && !destinationIdFromSearchParams;
  const destinationIdInSync = destinationIdInBoth || destinationIdInNeither;

  useEffect(() => {
    const availableConnectorIds = { ...(sourceId ? { sourceId } : {}), ...(destinationId ? { destinationId } : {}) };

    // the source conditions are the top-level, with destination conditions nested inside
    if (sourceIdInSync && destinationIdInSync) {
      // no further action needed here
    } else if (sourceIdFromLocationState || destinationIdFromLocationState) {
      // location state takes precedence if search params and location.state have to be synced
      setSearchParams(availableConnectorIds);
    } else if (sourceIdFromSearchParams || destinationIdFromSearchParams) {
      // here, we have to simultaneously set matching query string and location.state
      // values to avoid a mutually recursive infinite loop:
      //   A: set location.state and rerender; GOTO B
      //   B: set query param and rerender; GOTO A
      navigate(`${location.search}`, { state: availableConnectorIds, replace: true });
    }
  }, [
    destinationId,
    destinationIdFromLocationState,
    destinationIdFromSearchParams,
    destinationIdInSync,
    location.search,
    navigate,
    setSearchParams,
    sourceId,
    sourceIdFromLocationState,
    sourceIdFromSearchParams,
    sourceIdInSync,
  ]);
  const source = useGetSource(sourceId);

  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const destination = useGetDestination(destinationId);
  const destinationDefinition = useDestinationDefinition(destination?.destinationDefinitionId);

  return { source, sourceDefinition, destination, destinationDefinition };
}

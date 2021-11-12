import React, { useCallback, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";
import { useAsyncFn } from "react-use";

import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import { DestinationResource } from "core/resources/Destination";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import useConnector from "hooks/services/useConnector";
import ConnectorsView from "./components/ConnectorsView";
import useWorkspace from "hooks/services/useWorkspace";

const DestinationsPage: React.FC = () => {
  const { workspace } = useWorkspace();
  const [isUpdateSuccess, setIsUpdateSuccess] = useState(false);
  const formatMessage = useIntl().formatMessage;
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );
  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});

  const updateDestinationDefinition = useFetcher(
    DestinationDefinitionResource.updateShape()
  );

  const { hasNewDestinationVersion } = useConnector();

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateDestinationDefinition(
          {},
          {
            destinationDefinitionId: id,
            dockerImageTag: version,
          }
        );
        setFeedbackList({ ...feedbackList, [id]: "success" });
      } catch (e) {
        const messageId =
          e.status === 422 ? "form.imageCannotFound" : "form.someError";
        setFeedbackList({
          ...feedbackList,
          [id]: formatMessage({ id: messageId }),
        });
      }
    },
    [feedbackList, formatMessage, updateDestinationDefinition]
  );

  const usedDestinationDefinitions = useMemo<DestinationDefinition[]>(() => {
    const destinationDefinitionMap = new Map<string, DestinationDefinition>();
    destinations.forEach((destination) => {
      const destinationDefinition = destinationDefinitions.find(
        (destinationDefinition) =>
          destinationDefinition.destinationDefinitionId ===
          destination.destinationDefinitionId
      );

      if (destinationDefinition) {
        destinationDefinitionMap.set(
          destinationDefinition.destinationDefinitionId,
          destinationDefinition
        );
      }
    });

    return Array.from(destinationDefinitionMap.values());
  }, [destinations, destinationDefinitions]);

  const { updateAllDestinationVersions } = useConnector();

  const [{ loading, error }, onUpdate] = useAsyncFn(async () => {
    setIsUpdateSuccess(false);
    await updateAllDestinationVersions();
    setIsUpdateSuccess(true);
    setTimeout(() => {
      setIsUpdateSuccess(false);
    }, 2000);
  }, [updateAllDestinationVersions]);

  return (
    <ConnectorsView
      type="destinations"
      isUpdateSuccess={isUpdateSuccess}
      hasNewConnectorVersion={hasNewDestinationVersion}
      onUpdateVersion={onUpdateVersion}
      usedConnectorsDefinitions={usedDestinationDefinitions}
      connectorsDefinitions={destinationDefinitions}
      loading={loading}
      error={error}
      onUpdate={onUpdate}
      feedbackList={feedbackList}
    />
  );
};

export default DestinationsPage;

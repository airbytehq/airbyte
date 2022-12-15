import React, { useCallback, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useAsyncFn } from "react-use";

import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import useConnector from "hooks/services/useConnector";
import {
  useDestinationDefinitionList,
  useUpdateDestinationDefinition,
} from "services/connector/DestinationDefinitionService";

import { useDestinationList } from "../../../../hooks/services/useDestinationHook";
import ConnectorsView from "./components/ConnectorsView";

const DestinationsPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SETTINGS_DESTINATION);

  const [isUpdateSuccess, setIsUpdateSuccess] = useState(false);
  const { formatMessage } = useIntl();
  const { destinationDefinitions } = useDestinationDefinitionList();
  const { destinations } = useDestinationList();

  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});

  const { mutateAsync: updateDestinationDefinition } = useUpdateDestinationDefinition();

  const { hasNewDestinationVersion } = useConnector();

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateDestinationDefinition({
          destinationDefinitionId: id,
          dockerImageTag: version,
        });
        setFeedbackList({ ...feedbackList, [id]: "success" });
      } catch (e) {
        const messageId = e.status === 422 ? "form.imageCannotFound" : "form.someError";
        setFeedbackList({
          ...feedbackList,
          [id]: formatMessage({ id: messageId }),
        });
      }
    },
    [feedbackList, formatMessage, updateDestinationDefinition]
  );

  const usedDestinationDefinitions = useMemo<DestinationDefinitionRead[]>(() => {
    const destinationDefinitionMap = new Map<string, DestinationDefinitionRead>();
    destinations.forEach((destination) => {
      const destinationDefinition = destinationDefinitions.find(
        (destinationDefinition) => destinationDefinition.destinationDefinitionId === destination.destinationDefinitionId
      );

      if (destinationDefinition) {
        destinationDefinitionMap.set(destinationDefinition.destinationDefinitionId, destinationDefinition);
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

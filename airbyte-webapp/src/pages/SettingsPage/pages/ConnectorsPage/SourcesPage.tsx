import React, { useCallback, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";
import { useAsyncFn } from "react-use";

import config from "config";
import SourceDefinitionResource, {
  SourceDefinition,
} from "core/resources/SourceDefinition";
import { SourceResource } from "core/resources/Source";
import useConnector from "components/hooks/services/useConnector";
import ConnectorsView from "./components/ConnectorsView";

const SourcesPage: React.FC = () => {
  const [isUpdateSuccess, setIsUpdateSucces] = useState(false);
  const formatMessage = useIntl().formatMessage;
  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );

  const updateSourceDefinition = useFetcher(
    SourceDefinitionResource.updateShape()
  );

  const { hasNewSourceVersion, updateAllSourceVersions } = useConnector();

  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});
  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateSourceDefinition(
          {},
          {
            sourceDefinitionId: id,
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
    [feedbackList, formatMessage, updateSourceDefinition]
  );

  const usedSourcesDefinitions: SourceDefinition[] = useMemo(() => {
    const sourceDefinitionMap = new Map<string, SourceDefinition>();
    sources.forEach((source) => {
      const sourceDefinition = sourceDefinitions.find(
        (sourceDefinition) =>
          sourceDefinition.sourceDefinitionId === source.sourceDefinitionId
      );

      if (sourceDefinition) {
        sourceDefinitionMap.set(source.sourceDefinitionId, sourceDefinition);
      }
    });

    return Array.from(sourceDefinitionMap.values());
  }, [sources, sourceDefinitions]);

  const [{ loading, error }, onUpdate] = useAsyncFn(async () => {
    setIsUpdateSucces(false);
    await updateAllSourceVersions();
    setIsUpdateSucces(true);
    setTimeout(() => {
      setIsUpdateSucces(false);
    }, 2000);
  }, [updateAllSourceVersions]);

  return (
    <ConnectorsView
      type="sources"
      loading={loading}
      error={error}
      isUpdateSuccess={isUpdateSuccess}
      hasNewConnectorVersion={hasNewSourceVersion}
      usedConnectorsDefinitions={usedSourcesDefinitions}
      connectorsDefinitions={sourceDefinitions}
      feedbackList={feedbackList}
      onUpdateVersion={onUpdateVersion}
      onUpdate={onUpdate}
    />
  );
};

export default SourcesPage;

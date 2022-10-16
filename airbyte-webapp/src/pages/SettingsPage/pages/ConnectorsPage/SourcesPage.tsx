import React, { useCallback, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useAsyncFn } from "react-use";

import { SourceDefinitionRead } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import useConnector from "hooks/services/useConnector";
import { useSourceList } from "hooks/services/useSourceHook";
import { useSourceDefinitionList, useUpdateSourceDefinition } from "services/connector/SourceDefinitionService";

import ConnectorsView from "./components/ConnectorsView";

const SourcesPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SETTINGS_SOURCE);

  const [isUpdateSuccess, setIsUpdateSucces] = useState(false);
  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});

  const { formatMessage } = useIntl();
  const { sources } = useSourceList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const { mutateAsync: updateSourceDefinition } = useUpdateSourceDefinition();

  const { hasNewSourceVersion, updateAllSourceVersions } = useConnector();

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateSourceDefinition({
          sourceDefinitionId: id,
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
    [feedbackList, formatMessage, updateSourceDefinition]
  );

  const usedSourcesDefinitions: SourceDefinitionRead[] = useMemo(() => {
    const sourceDefinitionMap = new Map<string, SourceDefinitionRead>();
    sources.forEach((source) => {
      const sourceDefinition = sourceDefinitions.find(
        (sourceDefinition) => sourceDefinition.sourceDefinitionId === source.sourceDefinitionId
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

import React, { useCallback, useMemo, useRef, useState } from "react";
import { useIntl } from "react-intl";
import { useAsyncFn } from "react-use";

import { SourceDefinitionRead } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useGetConnectorsOutOfDate, useUpdateSourceDefinitions } from "hooks/services/useConnector";
import { useSourceList } from "hooks/services/useSourceHook";
import { useSourceDefinitionList, useUpdateSourceDefinition } from "services/connector/SourceDefinitionService";

import ConnectorsView from "./components/ConnectorsView";

const SourcesPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SETTINGS_SOURCE);

  const [isUpdateSuccess, setIsUpdateSuccess] = useState(false);
  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});
  const feedbackListRef = useRef(feedbackList);
  feedbackListRef.current = feedbackList;

  const { formatMessage } = useIntl();
  const { sources } = useSourceList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const { mutateAsync: updateSourceDefinition } = useUpdateSourceDefinition();
  const [updatingDefinitionId, setUpdatingDefinitionId] = useState<string>();

  const { hasNewSourceVersion } = useGetConnectorsOutOfDate();
  const { updateAllSourceVersions } = useUpdateSourceDefinitions();

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        setUpdatingDefinitionId(id);
        await updateSourceDefinition({
          sourceDefinitionId: id,
          dockerImageTag: version,
        });
        setFeedbackList({ ...feedbackListRef.current, [id]: "success" });
      } catch (e) {
        const messageId = e.status === 422 ? "form.imageCannotFound" : "form.someError";
        setFeedbackList({
          ...feedbackListRef.current,
          [id]: formatMessage({ id: messageId }),
        });
      } finally {
        setUpdatingDefinitionId(undefined);
      }
    },
    [formatMessage, updateSourceDefinition]
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
    setIsUpdateSuccess(false);
    await updateAllSourceVersions();
    setIsUpdateSuccess(true);
    setTimeout(() => {
      setIsUpdateSuccess(false);
    }, 2000);
  }, [updateAllSourceVersions]);

  return (
    <ConnectorsView
      type="sources"
      loading={loading}
      updatingDefinitionId={updatingDefinitionId}
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

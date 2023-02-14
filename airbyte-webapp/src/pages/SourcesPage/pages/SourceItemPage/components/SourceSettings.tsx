import React, { useCallback, useEffect, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useOutletContext } from "react-router-dom";

import { ConnectionConfiguration } from "core/domain/connection";
import { SourceRead } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useDeleteSource, useInvalidateSource, useUpdateSource } from "hooks/services/useSourceHook";
import { useDeleteModal } from "hooks/useDeleteModal";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./SourceSettings.module.scss";

const SourceSettings: React.FC = () => {
  const { mutateAsync: updateSource } = useUpdateSource();
  const { mutateAsync: deleteSource } = useDeleteSource();
  const { setDocumentationPanelOpen } = useDocumentationPanelContext();
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();

  const { source } = useOutletContext<{ source: SourceRead }>();
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);

  // We load only connections attached to this source to be shown in the connections grid
  const { connections } = useConnectionList({ sourceId: [source.sourceId] });

  useTrackPage(PageTrackingCodes.SOURCE_ITEM_SETTINGS);
  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

  const sourceDefinitionSpecification = useGetSourceDefinitionSpecification(source.sourceDefinitionId);

  const reloadSource = useInvalidateSource(source.sourceId);

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    await updateSource({
      values,
      sourceId: source.sourceId,
    });
  };

  const onDelete = useCallback(async () => {
    clearFormChange(formId);
    await deleteSource({ connectionsWithSource: connections, source });
  }, [clearFormChange, connections, source, deleteSource, formId]);

  const modalAdditionalContent = useMemo<React.ReactNode>(() => {
    if (connections.length === 0) {
      return null;
    }
    return (
      <p>
        <FormattedMessage id="tables.affectedConnectionsOnDeletion" values={{ count: connections.length }} />
        {connections.map((connection) => (
          <>
            - <strong>{`${connection.name}\n`}</strong>
          </>
        ))}
      </p>
    );
  }, [connections]);

  const onDeleteClick = useDeleteModal("source", onDelete, modalAdditionalContent);

  return (
    <div className={styles.content}>
      <ConnectorCard
        formType="source"
        title={<FormattedMessage id="sources.sourceSettings" />}
        isEditMode
        formId={formId}
        availableConnectorDefinitions={[sourceDefinition]}
        selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
        selectedConnectorDefinitionId={sourceDefinitionSpecification.sourceDefinitionId}
        connector={source}
        reloadConfig={reloadSource}
        onSubmit={onSubmit}
        onDeleteClick={onDeleteClick}
      />
    </div>
  );
};

export default SourceSettings;

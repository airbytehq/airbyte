import React, { useEffect, useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { DeleteBlock } from "components/common/DeleteBlock";

import { ConnectionConfiguration } from "core/domain/connection";
import { SourceRead, WebBackendConnectionListItem } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useDeleteSource, useUpdateSource } from "hooks/services/useSourceHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./SourceSettings.module.scss";

interface SourceSettingsProps {
  currentSource: SourceRead;
  connectionsWithSource: WebBackendConnectionListItem[];
}

const SourceSettings: React.FC<SourceSettingsProps> = ({ currentSource, connectionsWithSource }) => {
  const { mutateAsync: updateSource } = useUpdateSource();
  const { mutateAsync: deleteSource } = useDeleteSource();
  const { setDocumentationPanelOpen } = useDocumentationPanelContext();
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();

  useTrackPage(PageTrackingCodes.SOURCE_ITEM_SETTINGS);
  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

  const sourceDefinitionSpecification = useGetSourceDefinitionSpecification(currentSource.sourceDefinitionId);

  const sourceDefinition = useSourceDefinition(currentSource.sourceDefinitionId);

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    await updateSource({
      values,
      sourceId: currentSource.sourceId,
    });
  };

  const onDelete = async () => {
    clearFormChange(formId);
    await deleteSource({ connectionsWithSource, source: currentSource });
  };

  const modalAdditionalContent = useMemo<React.ReactNode>(() => {
    if (connectionsWithSource.length === 0) {
      return null;
    }
    return (
      <p>
        <FormattedMessage id="tables.affectedConnectionsOnDeletion" values={{ count: connectionsWithSource.length }} />
        {connectionsWithSource.map((connection) => (
          <b>- {`${connection.name}\n`}</b>
        ))}
      </p>
    );
  }, [connectionsWithSource]);

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
        connector={currentSource}
        onSubmit={onSubmit}
      />
      <DeleteBlock modalAdditionalContent={modalAdditionalContent} type="source" onDelete={onDelete} />
    </div>
  );
};

export default SourceSettings;

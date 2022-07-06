import { faCopy } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import DeleteBlock from "components/DeleteBlock";
import TitleBlock from "components/TitleBlock/TitleBlock";

import { ConnectionConfiguration } from "core/domain/connection";
import { SourceRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useDeleteSource, useUpdateSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./SourceSettings.module.scss";

interface SourceSettingsProps {
  currentSource: SourceRead;
  connectionsWithSource: WebBackendConnectionRead[];
}

const SourceSettings: React.FC<SourceSettingsProps> = ({ currentSource, connectionsWithSource }) => {
  const { mutateAsync: updateSource } = useUpdateSource();
  const { mutateAsync: deleteSource } = useDeleteSource();
  const { push } = useRouter();

  const { setDocumentationPanelOpen } = useDocumentationPanelContext();

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
  }) =>
    await updateSource({
      values,
      sourceId: currentSource.sourceId,
    });

  const onDelete = () => deleteSource({ connectionsWithSource, source: currentSource });

  const moveToClonePage = () => push(`../../${RoutePaths.SourceClone}/${currentSource.sourceId}`);

  const Actions = (
    <Button className={styles.cloneButton} light onClick={moveToClonePage}>
      <span className={styles.cloneText}>
        <FormattedMessage id="sources.cloneText" />
      </span>
      <FontAwesomeIcon className={styles.cloneIcon} icon={faCopy} />
    </Button>
  );

  return (
    <div className={styles.content}>
      <TitleBlock title={<FormattedMessage id="sources.sourceSettings" />} actions={Actions} />
      <ConnectorCard
        isEditMode
        onSubmit={onSubmit}
        formType="source"
        connector={currentSource}
        availableServices={[sourceDefinition]}
        formValues={{
          ...currentSource,
          serviceType: currentSource.sourceDefinitionId,
        }}
        selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
      />
      <DeleteBlock type="source" onDelete={onDelete} />
    </div>
  );
};

export default SourceSettings;

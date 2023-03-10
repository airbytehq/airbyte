import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { SourceRead } from "core/request/AirbyteClient";
import { SourceCloneRequestBody } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useUniqueFormId } from "hooks/services/FormChangeTracker"; // useFormChangeTrackerService
import { useCloneSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import styles from "./SourceCopy.module.scss";

interface SourceSettingsProps {
  currentSource: SourceRead;
  errorMessage?: JSX.Element | string | null;
  onBack?: () => void;
  formValues?: ServiceFormValues | null;
  afterSubmit?: () => void;
  onShowLoading?: (
    isLoading: boolean,
    formValues: ServiceFormValues | null,
    error: JSX.Element | string | null
  ) => void;
}

const SourceCopy: React.FC<SourceSettingsProps> = ({
  currentSource,
  errorMessage,
  formValues,
  onBack,
  onShowLoading,
  afterSubmit,
}) => {
  const { mutateAsync: cloneSource } = useCloneSource();
  const { setDocumentationPanelOpen } = useDocumentationPanelContext();
  const formId = useUniqueFormId();
  const { query } = useRouter<{ id: string }, { id: string; "*": string }>();
  // const { clearFormChange } = useFormChangeTrackerService();

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
    const cloneSourceData: SourceCloneRequestBody = {
      sourceCloneId: query.id,
      sourceConfiguration: {
        name: values.name,
        connectionConfiguration: values.connectionConfiguration,
      },
    };
    await cloneSource({ source: cloneSourceData });
    if (afterSubmit) {
      afterSubmit();
    }
  };

  const defaultFormValues = formValues?.serviceType
    ? formValues
    : { ...currentSource, serviceType: currentSource.sourceDefinitionId, name: `${currentSource.name} (Copy)` };

  return (
    <div className={styles.content}>
      <ConnectorCard
        formId={formId}
        title={<FormattedMessage id="sources.sourceSettings" />}
        onSubmit={onSubmit}
        isCopyMode
        formType="source"
        connector={currentSource}
        availableServices={[sourceDefinition]}
        formValues={defaultFormValues}
        selectedConnectorDefinitionSpecification={sourceDefinitionSpecification}
        onBack={onBack}
        onShowLoading={onShowLoading}
        errorMessage={errorMessage}
      />
    </div>
  );
};

export default SourceCopy;

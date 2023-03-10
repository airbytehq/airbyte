import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { SourceRead } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useUniqueFormId } from "hooks/services/FormChangeTracker"; // useFormChangeTrackerService
import { useUpdateSource } from "hooks/services/useSourceHook"; //
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecification } from "services/connector/SourceDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import styles from "./SourceSettings.module.scss";

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

const SourceSettings: React.FC<SourceSettingsProps> = ({
  currentSource,
  errorMessage,
  formValues,
  onBack,
  onShowLoading,
  afterSubmit,
}) => {
  const { mutateAsync: updateSource } = useUpdateSource();
  const { setDocumentationPanelOpen } = useDocumentationPanelContext();
  const formId = useUniqueFormId();
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
    await updateSource({
      values,
      sourceId: currentSource.sourceId,
    });
    if (afterSubmit) {
      afterSubmit();
    }
  };

  const defaultFormValues = formValues?.serviceType
    ? formValues
    : { ...currentSource, serviceType: currentSource.sourceDefinitionId };

  return (
    <div className={styles.content}>
      <ConnectorCard
        formId={formId}
        title={<FormattedMessage id="sources.sourceSettings" />}
        isEditMode
        onSubmit={onSubmit}
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

export default SourceSettings;

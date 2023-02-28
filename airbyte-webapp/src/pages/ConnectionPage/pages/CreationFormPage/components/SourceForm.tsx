import React, { useEffect, useState } from "react";

import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { SourceForm } from "pages/SourcesPage/pages/CreateSourcePage/components/SourceForm";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
interface ConnectionCreateSourceFormProps {
  afterSubmit: () => void;
  onShowLoading?: (isLoading: boolean, formValues: ServiceFormValues, error: JSX.Element | string | null) => void;
  onBack?: () => void;
  fetchingConnectorError?: JSX.Element | string | null;
  formValues: ServiceFormValues;
}

export const ConnectionCreateSourceForm: React.FC<ConnectionCreateSourceFormProps> = ({
  afterSubmit,
  onShowLoading,
  onBack,
  formValues,
  fetchingConnectorError,
}) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: createSource } = useCreateSource();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const sourceConnector = sourceDefinitions.find((item) => item.sourceDefinitionId === values.serviceType);
    if (!sourceConnector) {
      // Unsure if this can happen, but the types want it defined
      throw new Error("No Connector Found");
    }
    const result = await createSource({ values, sourceConnector });
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      push(
        {},
        {
          state: {
            ...(location.state as Record<string, unknown>),
            sourceId: result.sourceId,
          },
        }
      );
      afterSubmit();
    }, 2000);
  };

  const { setDocumentationPanelOpen } = useDocumentationPanelContext();

  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

  return (
    <SourceForm
      onSubmit={onSubmitSourceStep}
      sourceDefinitions={sourceDefinitions}
      hasSuccess={successRequest}
      onShowLoading={onShowLoading}
      onBack={onBack}
      error={fetchingConnectorError}
      formValues={formValues}
    />
  );
};

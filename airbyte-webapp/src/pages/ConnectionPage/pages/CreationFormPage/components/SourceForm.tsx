import React, { useState } from "react";

// TODO: create separate component for source and destinations forms
import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import SourceForm from "pages/SourcesPage/pages/CreateSourcePage/components/SourceForm";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

type IProps = {
  afterSubmit: () => void;
};

const SourceFormComponent: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: createSource } = useCreateSource();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === values.serviceType);
    const result = await createSource({ values, sourceConnector: connector });
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

  return <SourceForm onSubmit={onSubmitSourceStep} sourceDefinitions={sourceDefinitions} hasSuccess={successRequest} />;
};

export default SourceFormComponent;

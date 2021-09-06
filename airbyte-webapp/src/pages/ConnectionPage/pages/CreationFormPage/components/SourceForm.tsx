import React, { useState } from "react";
import { useResource } from "rest-hooks";

import useRouter from "hooks/useRouter";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import useSource from "hooks/services/useSourceHook";

// TODO: create separate component for source and destinations forms
import SourceForm from "pages/SourcesPage/pages/CreateSourcePage/components/SourceForm";
import { ConnectionConfiguration } from "core/domain/connection";
import useWorkspace from "hooks/services/useWorkspace";

type IProps = {
  afterSubmit: () => void;
};

const SourceFormComponent: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState(null);
  const { workspace } = useWorkspace();
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );
  const { createSource } = useSource();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setErrorStatusRequest(null);

    const connector = sourceDefinitions.find(
      (item) => item.sourceDefinitionId === values.serviceType
    );
    try {
      const result = await createSource({ values, sourceConnector: connector });
      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        afterSubmit();
        push({
          state: {
            ...(location.state as Record<string, unknown>),
            sourceId: result.sourceId,
          },
        });
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  return (
    <SourceForm
      onSubmit={onSubmitSourceStep}
      sourceDefinitions={sourceDefinitions}
      hasSuccess={successRequest}
      error={errorStatusRequest}
    />
  );
};

export default SourceFormComponent;

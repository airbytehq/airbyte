import React, { useState } from "react";
import { useResource } from "rest-hooks";

import useRouter from "hooks/useRouter";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useDestination from "hooks/services/useDestinationHook";

// TODO: create separate component for source and destinations forms
import DestinationForm from "pages/DestinationPage/pages/CreateDestinationPage/components/DestinationForm";
import { ConnectionConfiguration } from "core/domain/connection";
import useWorkspace from "hooks/services/useWorkspace";

type IProps = {
  afterSubmit: () => void;
};

const CreateDestinationPage: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const { workspace } = useWorkspace();
  const [successRequest, setSuccessRequest] = useState(false);

  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );
  const { createDestination } = useDestination();

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = destinationDefinitions.find(
      (item) => item.destinationDefinitionId === values.serviceType
    );
    const result = await createDestination({
      values,
      destinationConnector: connector,
    });
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      push(
        {},
        {
          state: {
            ...(location.state as Record<string, unknown>),
            destinationId: result.destinationId,
          },
        }
      );
      afterSubmit();
    }, 2000);
  };

  return (
    <DestinationForm
      onSubmit={onSubmitDestinationForm}
      destinationDefinitions={destinationDefinitions}
      hasSuccess={successRequest}
    />
  );
};

export default CreateDestinationPage;

import React, { useState } from "react";

import useRouter from "hooks/useRouter";
import useDestination from "hooks/services/useDestinationHook";

// TODO: create separate component for source and destinations forms
import DestinationForm from "pages/DestinationPage/pages/CreateDestinationPage/components/DestinationForm";
import { ConnectionConfiguration } from "core/domain/connection";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

type IProps = {
  afterSubmit: () => void;
};

const CreateDestinationPage: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState(null);

  const { destinationDefinitions } = useDestinationDefinitionList();
  const { createDestination } = useDestination();

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setErrorStatusRequest(null);

    const connector = destinationDefinitions.find(
      (item) => item.destinationDefinitionId === values.serviceType
    );
    try {
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
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  return (
    <DestinationForm
      onSubmit={onSubmitDestinationForm}
      destinationDefinitions={destinationDefinitions}
      hasSuccess={successRequest}
      error={errorStatusRequest}
    />
  );
};

export default CreateDestinationPage;

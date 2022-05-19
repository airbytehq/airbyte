import React, { useState } from "react";

// TODO: create separate component for source and destinations forms
import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import useRouter from "hooks/useRouter";
import DestinationForm from "pages/DestinationPage/pages/CreateDestinationPage/components/DestinationForm";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

type IProps = {
  afterSubmit: () => void;
};

const CreateDestinationPage: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);

  const { destinationDefinitions } = useDestinationDefinitionList();
  const { mutateAsync: createDestination } = useCreateDestination();

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === values.serviceType);
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

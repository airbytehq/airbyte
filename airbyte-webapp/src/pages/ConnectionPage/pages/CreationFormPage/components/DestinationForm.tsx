import React, { useMemo, useState } from "react";
import { useResource } from "rest-hooks";

import useRouter from "../../../../../components/hooks/useRouterHook";
import config from "../../../../../config";
import DestinationDefinitionResource from "../../../../../core/resources/DestinationDefinition";
import useDestination from "../../../../../components/hooks/services/useDestinationHook";

// TODO: create separate component for source and destinations forms
import DestinationForm from "../../../../DestinationPage/pages/CreateDestinationPage/components/DestinationForm";

type IProps = {
  afterSubmit: () => void;
};

const CreateDestinationPage: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const { createDestination } = useDestination();

  const destinationsDropDownData = useMemo(
    () =>
      destinationDefinitions.map(item => ({
        text: item.name,
        value: item.destinationDefinitionId,
        img: "/default-logo-catalog.svg"
      })),
    [destinationDefinitions]
  );

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    const connector = destinationDefinitions.find(
      item => item.destinationDefinitionId === values.serviceType
    );
    setErrorStatusRequest(0);
    try {
      const result = await createDestination({
        values,
        destinationConnector: connector
      });
      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        afterSubmit();
        push({
          state: { ...location.state, destinationId: result.destinationId }
        });
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  return (
    <DestinationForm
      onSubmit={onSubmitDestinationForm}
      dropDownData={destinationsDropDownData}
      hasSuccess={successRequest}
      errorStatus={errorStatusRequest}
    />
  );
};

export default CreateDestinationPage;

import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "../../../../components/PageTitle";
import DestinationForm from "./components/DestinationForm";
import { Routes } from "../../../routes";
import useRouter from "../../../../components/hooks/useRouterHook";
import config from "../../../../config";
import DestinationDefinitionResource from "../../../../core/resources/DestinationDefinition";
import useDestination from "../../../../components/hooks/services/useDestinationHook";
import { FormPageContent } from "../../../../components/SourceAndDestinationsBlocks";

const CreateDestinationPage: React.FC = () => {
  const { push } = useRouter();
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
        push(`${Routes.Destination}/${result.destinationId}`);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  return (
    <>
      <PageTitle
        withLine
        title={<FormattedMessage id="destinations.newDestinationTitle" />}
      />
      <FormPageContent>
        <DestinationForm
          onSubmit={onSubmitDestinationForm}
          dropDownData={destinationsDropDownData}
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
        />
      </FormPageContent>
    </>
  );
};

export default CreateDestinationPage;

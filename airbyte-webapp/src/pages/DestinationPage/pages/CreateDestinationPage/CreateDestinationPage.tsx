import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import DestinationForm from "./components/DestinationForm";
import { Routes } from "../../../routes";
import useRouter from "components/hooks/useRouterHook";
import config from "config";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useDestination from "components/hooks/services/useDestinationHook";
import { FormPageContent } from "components/SourceAndDestinationsBlocks";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";

const CreateDestinationPage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );
  const { createDestination } = useDestination();

  const destinationsDropDownData = useMemo(
    () =>
      destinationDefinitions.map((item) => ({
        text: item.name,
        value: item.destinationDefinitionId,
        img: "/default-logo-catalog.svg",
      })),
    [destinationDefinitions]
  );

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = destinationDefinitions.find(
      (item) => item.destinationDefinitionId === values.serviceType
    );
    setErrorStatusRequest(null);
    try {
      const result = await createDestination({
        values,
        destinationConnector: connector,
      });
      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        push(`${Routes.Destination}/${result.destinationId}`);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e);
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
          afterSelectConnector={() => setErrorStatusRequest(null)}
          onSubmit={onSubmitDestinationForm}
          dropDownData={destinationsDropDownData}
          hasSuccess={successRequest}
          error={errorStatusRequest}
          jobInfo={errorStatusRequest?.response}
        />
      </FormPageContent>
    </>
  );
};

export default CreateDestinationPage;

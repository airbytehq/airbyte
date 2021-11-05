import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { Routes } from "../../../routes";
import PageTitle from "components/PageTitle";
import DestinationForm from "./components/DestinationForm";
import useRouter from "hooks/useRouter";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useDestination from "hooks/services/useDestinationHook";
import { FormPageContent } from "components/ConnectorBlocks";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import HeadTitle from "components/HeadTitle";
import useWorkspace from "hooks/services/useWorkspace";

const CreateDestinationPage: React.FC = () => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

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
      <HeadTitle titles={[{ id: "destinations.newDestinationTitle" }]} />
      <PageTitle
        withLine
        title={<FormattedMessage id="destinations.newDestinationTitle" />}
      />
      <FormPageContent>
        <DestinationForm
          afterSelectConnector={() => setErrorStatusRequest(null)}
          onSubmit={onSubmitDestinationForm}
          destinationDefinitions={destinationDefinitions}
          hasSuccess={successRequest}
          error={errorStatusRequest}
          jobInfo={errorStatusRequest?.response}
        />
      </FormPageContent>
    </>
  );
};

export default CreateDestinationPage;

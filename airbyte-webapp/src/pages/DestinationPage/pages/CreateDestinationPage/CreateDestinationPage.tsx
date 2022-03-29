import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import PageTitle from "components/PageTitle";
import DestinationForm from "./components/DestinationForm";
import useRouter from "hooks/useRouter";
import useDestination from "hooks/services/useDestinationHook";
import { FormPageContent } from "components/ConnectorBlocks";
import { ConnectionConfiguration } from "core/domain/connection";
import HeadTitle from "components/HeadTitle";
import { JobInfo } from "core/domain/job";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

const CreateDestinationPage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

  const { destinationDefinitions } = useDestinationDefinitionList();
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
        push(`../${result.destinationId}`);
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
        />
      </FormPageContent>
    </>
  );
};

export default CreateDestinationPage;

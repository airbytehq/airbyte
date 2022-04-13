import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";

import { FormPageContent } from "components/ConnectorBlocks";
import DocumentationPanel from "components/DocumentationPanel";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";

import DestinationForm from "./components/DestinationForm";

const CreateDestinationPage: React.FC = () => {
  const { location, push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);

  const { destinationDefinitions } = useDestinationDefinitionList();
  const { mutateAsync: createDestination } = useCreateDestination();

  const hasDestinationDefinitionId = (state: unknown): state is { destinationDefinitionId: string } => {
    return (
      typeof state === "object" &&
      state !== null &&
      typeof (state as { destinationDefinitionId?: string }).destinationDefinitionId === "string"
    );
  };

  const [destinationDefinitionId, setDestinationDefinitionId] = useState<string | null>(
    hasDestinationDefinitionId(location.state) ? location.state.destinationDefinitionId : null
  );

  const {
    data: destinationDefinitionSpecification,
    isLoading,
    error: destinationDefinitionError,
  } = useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);

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
      push(`../${result.destinationId}`);
    }, 2000);
  };

  const selectedService = destinationDefinitions.find(
    (item) => item.destinationDefinitionId === destinationDefinitionId
  );

  return (
    <>
      <HeadTitle titles={[{ id: "destinations.newDestinationTitle" }]} />
      <ReflexContainer orientation="vertical" windowResizeAware={true}>
        <ReflexElement className="left-pane">
          <PageTitle withLine title={<FormattedMessage id="destinations.newDestinationTitle" />} />
          <FormPageContent>
            <DestinationForm
              onSubmit={onSubmitDestinationForm}
              destinationDefinitions={destinationDefinitions}
              setDestinationDefinitionId={setDestinationDefinitionId}
              destinationDefinitionSpecification={destinationDefinitionSpecification}
              destinationDefinitionError={destinationDefinitionError}
              hasSuccess={successRequest}
              isLoading={isLoading}
            />
          </FormPageContent>
        </ReflexElement>
        <ReflexSplitter />
        <ReflexElement className="right-pane" maxSize={800}>
          {selectedService ? (
            <DocumentationPanel
              onClose={() => null}
              selectedService={selectedService}
              documentationUrl={selectedService?.documentationUrl || ""}
            />
          ) : (
            "GET STARTED"
          )}
        </ReflexElement>
      </ReflexContainer>
    </>
  );
};

export default CreateDestinationPage;

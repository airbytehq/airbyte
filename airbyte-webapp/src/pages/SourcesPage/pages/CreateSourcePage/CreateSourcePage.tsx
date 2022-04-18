import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";

import { PageTitle } from "components";
import { FormPageContent } from "components/ConnectorBlocks";
import DocumentationPanel from "components/DocumentationPanel/DocumentationPanel";
import HeadTitle from "components/HeadTitle";

import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";

import SourceForm from "./components/SourceForm";

const CreateSourcePage: React.FC = () => {
  const { location, push } = useRouter();

  const [successRequest, setSuccessRequest] = useState(false);

  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: createSource } = useCreateSource();

  const hasSourceDefinitionId = (state: unknown): state is { sourceDefinitionId: string } => {
    return (
      typeof state === "object" &&
      state !== null &&
      typeof (state as { sourceDefinitionId?: string }).sourceDefinitionId === "string"
    );
  };

  const [sourceDefinitionId, setSourceDefinitionId] = useState<string | null>(
    hasSourceDefinitionId(location.state) ? location.state.sourceDefinitionId : null
  );

  const {
    data: sourceDefinitionSpecification,
    error: sourceDefinitionError,
    isLoading,
  } = useGetSourceDefinitionSpecificationAsync(sourceDefinitionId);

  const onSubmitSourceForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === values.serviceType);
    const result = await createSource({ values, sourceConnector: connector });
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      push(`../${result.sourceId}`);
    }, 2000);
  };

  const selectedService = sourceDefinitions.find((item) => item.sourceDefinitionId === sourceDefinitionId);

  return (
    <>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />
      <ReflexContainer orientation="vertical" windowResizeAware={true}>
        <ReflexElement className="left-pane">
          <PageTitle withLine title={<FormattedMessage id="sources.newSourceTitle" />} />
          <FormPageContent>
            <SourceForm
              onSubmit={onSubmitSourceForm}
              sourceDefinitions={sourceDefinitions}
              setSourceDefinitionId={setSourceDefinitionId}
              sourceDefinitionSpecification={sourceDefinitionSpecification}
              sourceDefinitionError={sourceDefinitionError}
              hasSuccess={successRequest}
              isLoading={isLoading}
            />
          </FormPageContent>{" "}
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

export default CreateSourcePage;

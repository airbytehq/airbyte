import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import styled from "styled-components";

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

const PanelGrabber = styled.div`
  height: 100vh;
  padding: 6px;
  display: flex;
`;

const GrabberHandle = styled(FontAwesomeIcon)`
  margin: auto;
  height: 25px;
  color: ${({ theme }) => theme.greyColor20};
`;

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
          <PageTitle title={null} middleTitleBlock={<FormattedMessage id="sources.newSourceTitle" />} />
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
          </FormPageContent>
        </ReflexElement>

        <ReflexSplitter style={{ border: 0, background: "rgba(255, 165, 0, 0)" }}>
          <PanelGrabber>
            <GrabberHandle icon={faGripLinesVertical} size={"1x"} />
          </PanelGrabber>
        </ReflexSplitter>
        <ReflexElement className="right-pane" size={1000}>
          <DocumentationPanel
            onClose={() => null}
            selectedService={selectedService}
            documentationUrl={selectedService?.documentationUrl || ""}
          />
        </ReflexElement>
      </ReflexContainer>
    </>
  );
};

export default CreateSourcePage;

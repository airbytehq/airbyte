import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { FormPageContent } from "components/ConnectorBlocks";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { ConnectionConfiguration } from "core/domain/connection";
import { SourceRead } from "core/request/AirbyteClient";
import { useCloneSource, useGetSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationWrapper";

import { CloneSourceForm } from "./components/CloneSourceForm";

const CloneSourcePage: React.FC = () => {
  const { push, query } = useRouter();
  const { sourceCloneId } = query;
  const [successRequest, setSuccessRequest] = useState(false);

  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: cloneSource } = useCloneSource();
  const source = useGetSource(sourceCloneId) as SourceRead;

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === values.serviceType);
    if (!connector) {
      // Unsure if this can happen, but the types want it defined
      throw new Error("No Connector Found");
    }
    const result = await cloneSource({ sourceCloneId: source.sourceId, sourceConfiguration: values });
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      push(`../${result.sourceId}`);
    }, 2000);
  };

  return (
    <>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />
      <ConnectorDocumentationWrapper>
        <PageTitle title={null} middleTitleBlock={<FormattedMessage id="sources.cloneSourceTitle" />} />
        <FormPageContent>
          <CloneSourceForm
            sourceCloneId={sourceCloneId}
            onSubmit={onSubmitSourceStep}
            sourceDefinitions={sourceDefinitions}
            hasSuccess={successRequest}
          />
        </FormPageContent>
      </ConnectorDocumentationWrapper>
    </>
  );
};

export default CloneSourcePage;

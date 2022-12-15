import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { CloudInviteUsersHint } from "components/CloudInviteUsersHint";
import { HeadTitle } from "components/common/HeadTitle";
import { FormPageContent } from "components/ConnectorBlocks";
import { PageHeader } from "components/ui/PageHeader";

import { ConnectionConfiguration } from "core/domain/connection";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCreateSource } from "hooks/services/useSourceHook";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationWrapper";

import { SourceForm } from "./components/SourceForm";

const CreateSourcePage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SOURCE_NEW);
  const navigate = useNavigate();
  const [successRequest, setSuccessRequest] = useState(false);

  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: createSource } = useCreateSource();

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
    const result = await createSource({ values, sourceConnector: connector });
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      navigate(`../${result.sourceId}`);
    }, 2000);
  };

  return (
    <>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />{" "}
      <ConnectorDocumentationWrapper>
        <PageHeader title={null} middleTitleBlock={<FormattedMessage id="sources.newSourceTitle" />} />
        <FormPageContent>
          <SourceForm onSubmit={onSubmitSourceStep} sourceDefinitions={sourceDefinitions} hasSuccess={successRequest} />
          <CloudInviteUsersHint connectorType="source" />
        </FormPageContent>
      </ConnectorDocumentationWrapper>
    </>
  );
};

export default CreateSourcePage;

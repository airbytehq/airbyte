import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import SourceForm from "./components/SourceForm";
import useRouter from "hooks/useRouter";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import useSource from "hooks/services/useSourceHook";
import { FormPageContent } from "components/ConnectorBlocks";
import { ConnectionConfiguration } from "core/domain/connection";
import HeadTitle from "components/HeadTitle";
import useWorkspace from "hooks/services/useWorkspace";

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);

  const { workspace } = useWorkspace();

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );
  const { createSource } = useSource();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = sourceDefinitions.find(
      (item) => item.sourceDefinitionId === values.serviceType
    );
    const result = await createSource({ values, sourceConnector: connector });
    setSuccessRequest(true);
    setTimeout(() => {
      setSuccessRequest(false);
      push(`../${result.sourceId}`);
    }, 2000);
  };

  return (
    <>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />
      <PageTitle
        withLine
        title={<FormattedMessage id="sources.newSourceTitle" />}
      />
      <FormPageContent>
        <SourceForm
          onSubmit={onSubmitSourceStep}
          sourceDefinitions={sourceDefinitions}
          hasSuccess={successRequest}
        />
      </FormPageContent>
    </>
  );
};

export default CreateSourcePage;

import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import SourceForm from "./components/SourceForm";
import { Routes } from "../../../routes";
import useRouter from "hooks/useRouter";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import useSource from "hooks/services/useSourceHook";
import { FormPageContent } from "components/ConnectorBlocks";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";
import HeadTitle from "components/HeadTitle";
import useWorkspace from "hooks/services/useWorkspace";

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

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
    setErrorStatusRequest(null);
    try {
      const result = await createSource({ values, sourceConnector: connector });
      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        push(`${Routes.Source}/${result.sourceId}`);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e);
    }
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
          afterSelectConnector={() => setErrorStatusRequest(null)}
          onSubmit={onSubmitSourceStep}
          sourceDefinitions={sourceDefinitions}
          hasSuccess={successRequest}
          error={errorStatusRequest}
          jobInfo={errorStatusRequest?.response}
        />
      </FormPageContent>
    </>
  );
};

export default CreateSourcePage;

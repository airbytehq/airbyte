import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import SourceForm from "./components/SourceForm";
import { Routes } from "../../../routes";
import useRouter from "components/hooks/useRouterHook";
import config from "config";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import useSource from "components/hooks/services/useSourceHook";
import { FormPageContent } from "components/SourceAndDestinationsBlocks";
import { JobInfo } from "core/resources/Scheduler";
import { ConnectionConfiguration } from "core/domain/connection";

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<{
    status: number;
    response: JobInfo;
  } | null>(null);

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );
  const { createSource } = useSource();

  const sourcesDropDownData = useMemo(
    () =>
      sourceDefinitions.map((item) => ({
        text: item.name,
        value: item.sourceDefinitionId,
        img: "/default-logo-catalog.svg",
      })),
    [sourceDefinitions]
  );

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
      <PageTitle
        withLine
        title={<FormattedMessage id="sources.newSourceTitle" />}
      />
      <FormPageContent>
        <SourceForm
          afterSelectConnector={() => setErrorStatusRequest(null)}
          onSubmit={onSubmitSourceStep}
          dropDownData={sourcesDropDownData}
          hasSuccess={successRequest}
          error={errorStatusRequest}
          jobInfo={errorStatusRequest?.response}
        />
      </FormPageContent>
    </>
  );
};

export default CreateSourcePage;

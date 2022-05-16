import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { FormPageContent } from "components/ConnectorBlocks";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { ConnectionConfiguration } from "core/domain/connection";
import { useCreateSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import SourceForm from "./components/SourceForm";

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);

  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: createSource } = useCreateSource();

  const onSubmitSourceStep = async (values: {
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

  return (
    <>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />
      <PageTitle withLine title={<FormattedMessage id="sources.newSourceTitle" />} />
      <FormPageContent>
        <SourceForm onSubmit={onSubmitSourceStep} sourceDefinitions={sourceDefinitions} hasSuccess={successRequest} />
      </FormPageContent>
    </>
  );
};

export default CreateSourcePage;

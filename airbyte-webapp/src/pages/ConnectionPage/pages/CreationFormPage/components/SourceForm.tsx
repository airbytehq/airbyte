import React, { useMemo, useState } from "react";
import { useResource } from "rest-hooks";

import useRouter from "../../../../../components/hooks/useRouterHook";
import config from "../../../../../config";
import SourceDefinitionResource from "../../../../../core/resources/SourceDefinition";
import useSource from "../../../../../components/hooks/services/useSourceHook";

// TODO: create separate component for source and destinations forms
import SourceForm from "../../../../SourcesPage/pages/CreateSourcePage/components/SourceForm";

type IProps = {
  afterSubmit: () => void;
};

const SourceFormComponent: React.FC<IProps> = ({ afterSubmit }) => {
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const { createSource } = useSource();

  const sourcesDropDownData = useMemo(
    () =>
      sourceDefinitions.map(item => ({
        text: item.name,
        value: item.sourceDefinitionId,
        img: "/default-logo-catalog.svg"
      })),
    [sourceDefinitions]
  );

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    const connector = sourceDefinitions.find(
      item => item.sourceDefinitionId === values.serviceType
    );
    setErrorStatusRequest(0);
    try {
      const result = await createSource({ values, sourceConnector: connector });
      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        afterSubmit();
        push({
          state: { ...location.state, sourceId: result.sourceId }
        });
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  return (
    <SourceForm
      onSubmit={onSubmitSourceStep}
      dropDownData={sourcesDropDownData}
      hasSuccess={successRequest}
      errorStatus={errorStatusRequest}
    />
  );
};

export default SourceFormComponent;

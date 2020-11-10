import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";

import SourceResource, { Source } from "../../../../../core/resources/Source";
import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import useSource from "../../../../../components/hooks/services/useSourceHook";
import SourceDefinitionSpecificationResource from "../../../../../core/resources/SourceDefinitionSpecification";
import DeleteBlock from "../../../../../components/DeleteBlock";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import { Routes } from "../../../../routes";
import useRouter from "../../../../../components/hooks/useRouterHook";

const Content = styled.div`
  max-width: 639px;
  margin: 18px auto;
`;

type IProps = {
  currentSource: Source;
};

const SourceSettings: React.FC<IProps> = ({ currentSource }) => {
  const { push } = useRouter();

  const [saved, setSaved] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const { updateSource } = useSource();

  const sourceDelete = useFetcher(SourceResource.deleteShape());

  const sourceDefinitionSpecification = useResource(
    SourceDefinitionSpecificationResource.detailShape(),
    {
      sourceDefinitionId: currentSource.sourceDefinitionId
    }
  );

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    setErrorMessage("");

    const result = await updateSource({
      values,
      sourceId: currentSource.sourceId || ""
    });

    if (result.status === "failure") {
      setErrorMessage(result.message);
    } else {
      setSaved(true);
    }
  };

  const onDelete = async () => {
    await sourceDelete({
      sourceId: currentSource.sourceId
    });

    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Delete source",
      connector_source: currentSource.sourceName,
      connector_source_id: currentSource.sourceDefinitionId
    });

    push(Routes.Root);
  };

  return (
    <Content>
      <ContentCard title={<FormattedMessage id="sources.sourceSettings" />}>
        <ServiceForm
          isEditMode
          onSubmit={onSubmit}
          formType="source"
          dropDownData={[
            {
              value: currentSource.sourceDefinitionId || "",
              text: currentSource.sourceName || "",
              img: "/default-logo-catalog.svg"
            }
          ]}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
          errorMessage={errorMessage}
          formValues={{
            ...currentSource,
            serviceType: currentSource.sourceDefinitionId
          }}
          specifications={
            sourceDefinitionSpecification?.connectionSpecification
          }
        />
      </ContentCard>
      <DeleteBlock type="source" onDelete={onDelete} />
    </Content>
  );
};

export default SourceSettings;

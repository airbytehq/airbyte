import React, { useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { Source } from "../../../../../core/resources/Source";
import ContentCard from "../../../../../components/ContentCard";
import ServiceForm from "../../../../../components/ServiceForm";
import useSource from "../../../../../components/hooks/services/useSourceHook";
import SourceDefinitionSpecificationResource from "../../../../../core/resources/SourceDefinitionSpecification";
import DeleteBlock from "../../../../../components/DeleteBlock";
import { Connection } from "../../../../../core/resources/Connection";

const Content = styled.div`
  max-width: 813px;
  margin: 18px auto;
`;

type IProps = {
  currentSource: Source;
  connectionsWithSource: Connection[];
};

const SourceSettings: React.FC<IProps> = ({
  currentSource,
  connectionsWithSource
}) => {
  const [saved, setSaved] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const { updateSource, deleteSource } = useSource();

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
    await deleteSource({ connectionsWithSource, source: currentSource });
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

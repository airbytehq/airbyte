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
  const [errorMessage, setErrorMessage] = useState<string | React.ReactNode>(
    ""
  );

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
    try {
      await updateSource({
        values,
        sourceId: currentSource.sourceId,
        sourceDefinitionId: currentSource.sourceDefinitionId
      });

      setSaved(true);
    } catch (e) {
      const errorStatus = e.status;
      errorStatus === 0
        ? setErrorMessage("")
        : errorStatus === 400
        ? setErrorMessage(<FormattedMessage id="form.validationError" />)
        : setErrorMessage(<FormattedMessage id="form.someError" />);
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

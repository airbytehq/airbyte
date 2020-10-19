import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import DeleteSource from "./DeleteSource";
import ServiceForm from "../../../../../components/ServiceForm";
import { Connection } from "../../../../../core/resources/Connection";
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import SourceSpecificationResource from "../../../../../core/resources/SourceSpecification";
import useSource from "../../../../../components/hooks/services/useSourceHook";
import useConnection from "../../../../../components/hooks/services/useConnectionHook";

type IProps = {
  sourceData: Connection;
  afterDelete: () => void;
};

const Content = styled.div`
  max-width: 639px;
  margin: 18px auto;
`;

const SettingsView: React.FC<IProps> = ({ sourceData, afterDelete }) => {
  const [saved, setSaved] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const { updateSource } = useSource();
  const { updateConnection, updateStateConnection } = useConnection();

  const sourceSpecification = useResource(
    SourceSpecificationResource.detailShape(),
    sourceData.source
      ? {
          sourceId: sourceData.source.sourceId
        }
      : null
  );

  const schedule = FrequencyConfig.find(
    item => JSON.stringify(item.config) === JSON.stringify(sourceData.schedule)
  );

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    frequency?: string;
    connectionConfiguration?: any;
  }) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );
    setErrorMessage("");
    if (values.frequency !== schedule?.value) {
      await updateConnection({
        connectionId: sourceData.connectionId,
        syncSchema: sourceData.syncSchema,
        status: sourceData.status,
        schedule: frequencyData?.config || null
      });
    }

    const result = await updateSource({
      values,
      sourceImplementationId: sourceData.source?.sourceImplementationId || ""
    });

    await updateStateConnection({
      sourceData,
      sourceName: values.name,
      connectionConfiguration: values.connectionConfiguration,
      schedule: frequencyData?.config || null
    });

    if (result.status === "failure") {
      setErrorMessage(result.message);
    } else {
      setSaved(true);
    }
  };

  return (
    <Content>
      <ContentCard title={<FormattedMessage id="sources.sourceSettings" />}>
        <ServiceForm
          isEditMode
          onSubmit={onSubmit}
          formType="connection"
          dropDownData={[
            {
              value: sourceData.source?.sourceId || "",
              text: sourceData.source?.sourceName || "",
              img: "/default-logo-catalog.svg"
            }
          ]}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
          errorMessage={errorMessage}
          formValues={{
            ...sourceData.source?.connectionConfiguration,
            name: sourceData.source?.name,
            serviceType: sourceData.source?.sourceId || "",
            frequency: schedule?.value || ""
          }}
          specifications={sourceSpecification?.connectionSpecification}
        />
      </ContentCard>
      <DeleteSource
        afterDelete={afterDelete}
        sourceImplementationId={sourceData.source?.sourceImplementationId}
        connectionId={sourceData.connectionId}
      />
    </Content>
  );
};

export default SettingsView;

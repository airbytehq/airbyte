import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher, useResource } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import DeleteSource from "./DeleteSource";
import ServiceForm from "../../../../../components/ServiceForm";
import ConnectionResource, {
  Connection
} from "../../../../../core/resources/Connection";
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import SourceSpecificationResource from "../../../../../core/resources/SourceSpecification";
import SourceImplementationResource from "../../../../../core/resources/SourceImplementation";

type IProps = {
  sourceData: Connection;
};

const Content = styled.div`
  max-width: 639px;
  margin: 18px auto;
`;

const SettingsView: React.FC<IProps> = ({ sourceData }) => {
  const updateConnection = useFetcher(ConnectionResource.updateShape());
  const updateStateConnection = useFetcher(
    ConnectionResource.updateStateShape()
  );
  const updateSourceImplementation = useFetcher(
    SourceImplementationResource.updateShape()
  );

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

    if (values.frequency !== schedule?.value) {
      await updateConnection(
        {},
        {
          connectionId: sourceData.connectionId,
          syncSchema: sourceData.syncSchema,
          status: sourceData.status,
          schedule: frequencyData?.config
        }
      );
    }

    await updateSourceImplementation(
      {},
      {
        name: values.name,
        sourceImplementationId: sourceData.source?.sourceImplementationId,
        connectionConfiguration: values.connectionConfiguration
      }
    );

    await updateStateConnection(
      {},
      {
        ...sourceData,
        source: {
          ...sourceData.source,
          name: values.name,
          connectionConfiguration: values.connectionConfiguration
        }
      }
    );
  };

  return (
    <Content>
      <ContentCard title={<FormattedMessage id={"sources.sourceSettings"} />}>
        <ServiceForm
          onSubmit={onSubmit}
          formType="connection"
          dropDownData={[
            {
              value: sourceData.source?.sourceId || "",
              text: sourceData.source?.sourceName || "",
              img: "/default-logo-catalog.svg"
            }
          ]}
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
        sourceImplementationId={sourceData.source?.sourceImplementationId}
        connectionId={sourceData.connectionId}
      />
    </Content>
  );
};

export default SettingsView;

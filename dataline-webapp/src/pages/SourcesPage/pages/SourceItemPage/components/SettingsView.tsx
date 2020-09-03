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
  const updateSourceImplementation = useFetcher(
    SourceImplementationResource.updateShape()
  );
  const sourceImplementation = useResource(
    SourceImplementationResource.detailShape(),
    sourceData.source
      ? {
          sourceImplementationId: sourceData.source?.sourceImplementationId
        }
      : null
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
    item =>
      item.config.units === sourceData.schedule?.units &&
      item.config.timeUnit === sourceData.schedule?.timeUnit
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
        sourceImplementationId: sourceData.source?.sourceImplementationId,
        connectionConfiguration: values.connectionConfiguration
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
            ...sourceImplementation?.connectionConfiguration,
            name: sourceData.name,
            serviceType: sourceData.source?.sourceId || "",
            frequency: schedule?.value || ""
          }}
          specifications={sourceSpecification?.connectionSpecification}
        />
      </ContentCard>
      <DeleteSource />
    </Content>
  );
};

export default SettingsView;

import React from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import ContentCard from "../../../components/ContentCard";
import ConnectionBlock from "../../../components/ConnectionBlock";
import FrequencyForm from "../../../components/FrequencyForm";
import SourceResource from "../../../core/resources/Source";
import DestinationResource from "../../../core/resources/Destination";

type IProps = {
  onSubmit: (values: { frequency: string }) => void;
  currentSourceId: string;
  currentDestinationId: string;
};

const ConnectionStep: React.FC<IProps> = ({
  onSubmit,
  currentSourceId,
  currentDestinationId
}) => {
  const currentSource = useResource(SourceResource.detailShape(), {
    sourceId: currentSourceId
  });
  const currentDestination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestinationId
  });
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: currentSource.name }}
        itemTo={{ name: currentDestination.name }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <FrequencyForm onSubmit={onSubmit} />
      </ContentCard>
    </>
  );
};

export default ConnectionStep;

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
  errorStatus?: number;
};

const ConnectionStep: React.FC<IProps> = ({
  onSubmit,
  currentSourceId,
  currentDestinationId,
  errorStatus
}) => {
  const currentSource = useResource(SourceResource.detailShape(), {
    sourceId: currentSourceId
  });
  const currentDestination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestinationId
  });

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: currentSource.name }}
        itemTo={{ name: currentDestination.name }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <FrequencyForm onSubmit={onSubmit} errorMessage={errorMessage} />
      </ContentCard>
    </>
  );
};

export default ConnectionStep;

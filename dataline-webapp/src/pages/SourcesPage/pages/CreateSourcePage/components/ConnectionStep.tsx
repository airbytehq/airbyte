import React from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import FrequencyForm from "../../../../../components/FrequencyForm";
import { Destination } from "../../../../../core/resources/Destination";
import SourceResource from "../../../../../core/resources/Source";

type IProps = {
  onSubmit: () => void;
  destination: Destination;
  sourceId: string;
};

const CreateSourcePage: React.FC<IProps> = ({
  onSubmit,
  destination,
  sourceId
}) => {
  const source = useResource(SourceResource.detailShape(), {
    sourceId
  });
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: source.name }}
        itemTo={{ name: destination.name }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <FrequencyForm onSubmit={onSubmit} />
      </ContentCard>
    </>
  );
};

export default CreateSourcePage;

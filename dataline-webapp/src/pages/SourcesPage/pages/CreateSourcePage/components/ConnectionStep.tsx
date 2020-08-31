import React from "react";
import { FormattedMessage } from "react-intl";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import FrequencyForm from "../../../../../components/FrequencyForm";
import { Destination } from "../../../../../core/resources/Destination";
import { Source } from "../../../../../core/resources/Source";

type IProps = {
  onSubmit: () => void;
  destination: Destination;
  source?: Source;
};

const CreateSourcePage: React.FC<IProps> = ({
  onSubmit,
  destination,
  source
}) => {
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: source?.name || "" }}
        itemTo={{ name: destination.name }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <FrequencyForm onSubmit={onSubmit} />
      </ContentCard>
    </>
  );
};

export default CreateSourcePage;

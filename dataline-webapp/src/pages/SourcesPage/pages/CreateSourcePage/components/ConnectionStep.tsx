import React from "react";
import { FormattedMessage } from "react-intl";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import FrequencyForm from "../../../../../components/FrequencyForm";

type IProps = {
  onSubmit: () => void;
};

const CreateSourcePage: React.FC<IProps> = ({ onSubmit }) => {
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: "Test 1" }}
        itemTo={{ name: "Test 2" }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <FrequencyForm onSubmit={onSubmit} />
      </ContentCard>
    </>
  );
};

export default CreateSourcePage;

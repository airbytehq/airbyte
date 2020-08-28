import React from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import ConnectionBlock from "../../../components/ConnectionBlock";
import FrequencyForm from "../../../components/FrequencyForm";

type IProps = {
  onSubmit: (values: { frequency: string }) => void;
};

const ConnectionStep: React.FC<IProps> = ({ onSubmit }) => {
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

export default ConnectionStep;

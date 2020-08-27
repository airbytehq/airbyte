import React from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import ConnectionBlock from "../../../components/ConnectionBlock";

type IProps = {
  hasSuccess?: boolean;
  onSubmit: () => void;
  dropDownData: Array<{ text: string; value: string; img?: string }>;
  errorMessage?: React.ReactNode;
};

const Destination: React.FC<IProps> = ({
  onSubmit,
  dropDownData,
  hasSuccess,
  errorMessage
}) => {
  return (
    <>
      <ConnectionBlock itemFrom={{ name: "Test 1" }} />
      <ContentCard
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
      >
        <ServiceForm
          hasSuccess={hasSuccess}
          onSubmit={onSubmit}
          formType="destination"
          dropDownData={dropDownData}
          errorMessage={errorMessage}
        />
      </ContentCard>
    </>
  );
};

export default Destination;

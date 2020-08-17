import React from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";
import ConnectionBlock from "../../../components/ConnectionBlock";

type IProps = {
  onSubmit: () => void;
};

const Destination: React.FC<IProps> = ({ onSubmit }) => {
  const data = [
    {
      text: "destination 1",
      value: "1",
      img: "/default-logo-catalog.svg"
    },
    {
      text: "destination 2",
      value: "2",
      img: "/default-logo-catalog.svg"
    },
    {
      text: "destination 3",
      value: "3",
      img: "/default-logo-catalog.svg"
    },
    {
      text: "destination 4",
      value: "4",
      img: "/default-logo-catalog.svg"
    }
  ];

  return (
    <>
      <ConnectionBlock itemFrom={{ name: "Test 1" }} />
      <ContentCard
        title={<FormattedMessage id="onboarding.destinationSetUp" />}
      >
        <ServiceForm
          onSubmit={onSubmit}
          formType="destination"
          dropDownData={data}
        />
      </ContentCard>
    </>
  );
};

export default Destination;

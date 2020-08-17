import React from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import ServiceForm from "../../../components/ServiceForm";

type IProps = {
  onSubmit: () => void;
};

const SourceStep: React.FC<IProps> = ({ onSubmit }) => {
  const data = [
    {
      text: "connector 1",
      value: "1",
      img: "/default-logo-catalog.svg"
    },
    {
      text: "connector 2",
      value: "2",
      img: "/default-logo-catalog.svg"
    },
    {
      text: "connector 3",
      value: "3",
      img: "/default-logo-catalog.svg"
    },
    {
      text: "connector 4",
      value: "4",
      img: "/default-logo-catalog.svg"
    }
  ];

  return (
    <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
      <ServiceForm onSubmit={onSubmit} formType="source" dropDownData={data} />
    </ContentCard>
  );
};

export default SourceStep;

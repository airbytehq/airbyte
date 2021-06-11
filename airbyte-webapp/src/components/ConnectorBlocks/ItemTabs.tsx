import React from "react";
import { FormattedMessage } from "react-intl";

import StepsMenu from "components/StepsMenu";

export enum StepsTypes {
  OVERVIEW = "Overview",
  SETTINGS = "Settings",
}

type IProps = {
  currentStep: string;
  setCurrentStep: (step: string) => void;
};

const ItemTabs: React.FC<IProps> = ({ currentStep, setCurrentStep }) => {
  const steps = [
    {
      id: StepsTypes.OVERVIEW,
      name: <FormattedMessage id="tables.overview" />,
    },
    {
      id: StepsTypes.SETTINGS,
      name: <FormattedMessage id="tables.settings" />,
    },
  ];

  return (
    <StepsMenu
      lightMode
      data={steps}
      activeStep={currentStep}
      onSelect={setCurrentStep}
    />
  );
};

export default ItemTabs;

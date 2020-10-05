import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import MainPageWithScroll from "../../components/MainPageWithScroll";
import PageTitle from "../../components/PageTitle";
import StepsMenu from "../../components/StepsMenu";
import Button from "../../components/Button";

enum StepsTypes {
  SOURCES = "sources",
  DESTINATIONS = "destinations"
}

const AdminPage: React.FC = () => {
  const steps = [
    {
      id: StepsTypes.SOURCES,
      name: <FormattedMessage id={"admin.sources"} />
    },
    {
      id: StepsTypes.DESTINATIONS,
      name: <FormattedMessage id={"admin.destinations"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.SOURCES);
  const onSelectStep = (id: string) => setCurrentStep(id);

  return (
    <MainPageWithScroll
      title={
        <PageTitle
          withLine
          title={<FormattedMessage id={"sidebar.admin"} />}
          middleComponent={
            <StepsMenu
              lightMode
              data={steps}
              onSelect={onSelectStep}
              activeStep={currentStep}
            />
          }
          endComponent={
            currentStep === StepsTypes.SOURCES && (
              <Button>
                <FormattedMessage id="admin.newConnector" />
              </Button>
            )
          }
        />
      }
    />
  );
};

export default AdminPage;

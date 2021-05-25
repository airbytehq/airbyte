import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import StepsMenu from "components/StepsMenu";
import { StepMenuItem } from "components/StepsMenu/StepsMenu";
import LoadingPage from "components/LoadingPage";
import SourcesView from "./components/SourcesView";
import DestinationsView from "./components/DestinationsView";
import CreateConnector from "./components/CreateConnector";
import ConfigurationView from "./components/ConfigurationView";
import HeadTitle from "components/HeadTitle";

const Content = styled.div`
  padding-top: 4px;
  margin: 0 33px 0 27px;
  height: 100%;
`;

enum StepsTypes {
  SOURCES = "sources",
  DESTINATIONS = "destinations",
  CONFIGURATION = "configuration",
}

const AdminPage: React.FC = () => {
  const steps: StepMenuItem[] = [
    {
      id: StepsTypes.SOURCES,
      name: <FormattedMessage id="admin.sources" />,
    },
    {
      id: StepsTypes.DESTINATIONS,
      name: <FormattedMessage id="admin.destinations" />,
    },
    {
      id: StepsTypes.CONFIGURATION,
      name: <FormattedMessage id="admin.configuration" />,
    },
  ];
  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.SOURCES);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const renderStep = () => {
    if (currentStep === StepsTypes.SOURCES) {
      return <SourcesView />;
    }
    if (currentStep === StepsTypes.CONFIGURATION) {
      return <ConfigurationView />;
    }

    return <DestinationsView />;
  };

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.admin" }]} />}
      pageTitle={
        <PageTitle
          withLine
          title={<FormattedMessage id="sidebar.admin" />}
          middleComponent={
            <StepsMenu
              lightMode
              data={steps}
              onSelect={onSelectStep}
              activeStep={currentStep}
            />
          }
          endComponent={<CreateConnector type={currentStep} />}
        />
      }
    >
      <Content>
        <Suspense fallback={<LoadingPage />}>{renderStep()}</Suspense>
      </Content>
    </MainPageWithScroll>
  );
};

export default AdminPage;

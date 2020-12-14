import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import MainPageWithScroll from "../../components/MainPageWithScroll";
import PageTitle from "../../components/PageTitle";
import StepsMenu from "../../components/StepsMenu";
import LoadingPage from "../../components/LoadingPage";
import SourcesView from "./components/SourcesView";
import DestinationsView from "./components/DestinationsView";
import CreateConnector from "./components/CreateConnector";

const Content = styled.div`
  margin: 4px 33px 0 27px;
`;
enum StepsTypes {
  SOURCES = "sources",
  DESTINATIONS = "destinations"
}

const AdminPage: React.FC = () => {
  const steps = [
    {
      id: StepsTypes.SOURCES,
      name: <FormattedMessage id="admin.sources" />
    },
    {
      id: StepsTypes.DESTINATIONS,
      name: <FormattedMessage id="admin.destinations" />
    }
  ];
  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.SOURCES);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const renderStep = () => {
    if (currentStep === StepsTypes.SOURCES) {
      return <SourcesView />;
    }

    return <DestinationsView />;
  };

  return (
    <MainPageWithScroll
      title={
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

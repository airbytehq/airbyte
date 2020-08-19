import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import PageTitle from "../../../../components/PageTitle";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import useRouter from "../../../../components/hooks/useRouterHook";
import { Routes } from "../../../routes";
import StepsMenu from "../../../../components/StepsMenu";
import StatusView from "./components/StatusView";
import SettingsView from "./components/SettingsView";

const SourceItemPage: React.FC = () => {
  const [isEnabledSource, setIsEnabledSource] = useState(true);
  // TODO: change to real data
  const sourceData = {
    name: "Source Name",
    source: "Source",
    destination: "Destination",
    frequency: "5m",
    enabled: isEnabledSource
  };

  const steps = [
    {
      id: "status",
      name: <FormattedMessage id={"sources.status"} />
    },
    {
      id: "schema",
      name: <FormattedMessage id={"sources.schema"} />
    },
    {
      id: "settings",
      name: <FormattedMessage id={"sources.settings"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState("status");
  const onSelectStep = (id: string) => setCurrentStep(id);

  const { push, history } = useRouter();
  const onClickBack = () =>
    history.length > 2 ? history.goBack() : push(Routes.Source);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: onClickBack
    },
    { name: sourceData.name }
  ];

  const renderStep = () => {
    if (currentStep === "status") {
      return (
        <StatusView
          sourceData={sourceData}
          onEnabledChange={() => setIsEnabledSource(!isEnabledSource)}
        />
      );
    }
    if (currentStep === "schema") {
      return <div>schema</div>;
    }

    return <SettingsView sourceData={sourceData} />;
  };

  return (
    <>
      <PageTitle
        withLine
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={
          <StepsMenu
            lightMode
            data={steps}
            onSelect={onSelectStep}
            activeStep={currentStep}
          />
        }
      />
      {renderStep()}
    </>
  );
};

export default SourceItemPage;

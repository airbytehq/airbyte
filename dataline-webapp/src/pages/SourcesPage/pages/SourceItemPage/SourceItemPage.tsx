import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";

import PageTitle from "../../../../components/PageTitle";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import useRouter from "../../../../components/hooks/useRouterHook";
import { Routes } from "../../../routes";
import StepsMenu from "../../../../components/StepsMenu";
import StatusView from "./components/StatusView";
import SettingsView from "./components/SettingsView";
import SchemaView from "./components/SchemaView";
import ConnectionResource from "../../../../core/resources/Connection";

const SourceItemPage: React.FC = () => {
  const { query, push, history } = useRouter();

  const updateConnection = useFetcher(ConnectionResource.updateShape());

  const connection = useResource(ConnectionResource.detailShape(), {
    // @ts-ignore
    connectionId: query.id
  });

  // TODO: add redirect for connectionId with error

  // TODO: change to real data
  const sourceData = {
    name: "Source Name",
    source: "Source",
    destination: "Destination",
    frequency: "5m"
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

  const onClickBack = () =>
    history.length > 2 ? history.goBack() : push(Routes.Source);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: onClickBack
    },
    { name: connection.name }
  ];

  const onChangeStatus = async () => {
    await updateConnection(
      {},
      {
        connectionId: connection.connectionId,
        syncSchema: connection.syncSchema,
        schedule: connection.schedule,
        status: connection.status === "active" ? "inactive" : "active"
      }
    );
  };

  const renderStep = () => {
    if (currentStep === "status") {
      return (
        <StatusView sourceData={connection} onEnabledChange={onChangeStatus} />
      );
    }
    if (currentStep === "schema") {
      return <SchemaView />;
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

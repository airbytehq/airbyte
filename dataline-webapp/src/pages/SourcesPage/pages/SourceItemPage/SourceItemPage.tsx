import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";
import styled from "styled-components";

import PageTitle from "../../../../components/PageTitle";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import useRouter from "../../../../components/hooks/useRouterHook";
import { Routes } from "../../../routes";
import StepsMenu from "../../../../components/StepsMenu";
import StatusView from "./components/StatusView";
import SettingsView from "./components/SettingsView";
import SchemaView from "./components/SchemaView";
import ConnectionResource from "../../../../core/resources/Connection";

const Content = styled.div`
  overflow-y: auto;
  height: calc(100% - 67px);
  margin-top: -17px;
  padding-top: 17px;
`;

const Page = styled.div`
  overflow-y: hidden;
  height: 100%;
`;

const SourceItemPage: React.FC = () => {
  const { query, push, history } = useRouter();

  const updateConnection = useFetcher(ConnectionResource.updateShape());

  const connection = useResource(ConnectionResource.detailShape(), {
    // @ts-ignore
    connectionId: query.id
  });

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
      return (
        <SchemaView
          syncSchema={connection.syncSchema}
          connectionId={connection.connectionId}
          connectionStatus={connection.status}
        />
      );
    }

    return <SettingsView sourceData={connection} />;
  };

  return (
    <Page>
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
      <Content>{renderStep()}</Content>
    </Page>
  );
};

export default SourceItemPage;

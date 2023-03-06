import React, { useState, Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes, Navigate } from "react-router-dom";
import styled from "styled-components";

import { LoadingPage, DropDownRow } from "components";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import Breadcrumbs from "components/Breadcrumbs";
import { CreateStepTypes } from "components/ConnectionStep";
import { TableItemTitle, DefinitioDetails } from "components/ConnectorBlocks"; // StepsTypes
import { ConnectorIcon } from "components/ConnectorIcon";
import DeleteBlock from "components/DeleteBlock";
import { TabMenu, CategoryItem } from "components/TabMenu";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useDeleteDestination } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
import TestConnection from "views/Connector/TestConnection";

import { useGetDestination } from "../../../../hooks/services/useDestinationHook";
import DestinationConnectionTable from "./components/DestinationConnectionTable";
import DestinationSettings from "./components/DestinationSettings";

interface PageConfig {
  menuConfig: CategoryItem[];
}

interface SettingsPageProps {
  pageConfig?: PageConfig;
}

enum StepsTypes {
  CREATE_ENTITY = "createEntity",
  TEST_CONNECTION = "testConnection",
}

const Container = styled.div`
  padding: 0px 0px 10px 70px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
`;

const TabContainer = styled.div`
  margin: 20px 20px 40px 0;
`;

const TableContainer = styled.div`
  margin-right: 70px;
`;

const DestinationItemPage: React.FC<SettingsPageProps> = ({ pageConfig }) => {
  useTrackPage(PageTrackingCodes.DESTINATION_ITEM);
  const { params, push, pathname } = useRouter<unknown, { id: string; "*": string }>();
  // const currentStep = useMemo<string>(() => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]), [params]);
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_ENTITY);
  const [loadingStatus, setLoadingStatus] = useState<boolean>(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [destinationFormValues, setDestinationFormValues] = useState<ServiceFormValues | null>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const { sources } = useSourceList();
  const { sourceDefinitions } = useSourceDefinitionList();
  const destination = useGetDestination(params.id);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const { connections } = useConnectionList();
  const { mutateAsync: deleteDestination } = useDeleteDestination();

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="tables.allDestinations" />,
      onClick: () => push(".."),
    },
    { name: destination.name },
  ];

  const connectionsWithDestination = connections.filter(
    (connectionItem) => connectionItem.destinationId === destination.destinationId
  );

  const sourcesDropDownData = useMemo(
    () =>
      sources.map((item) => {
        const sourceDef = sourceDefinitions.find((sd) => sd.sourceDefinitionId === item.sourceDefinitionId);
        return {
          label: item.name,
          value: item.sourceId,
          img: <ConnectorIcon icon={sourceDef?.icon} />,
        };
      }),
    [sources, sourceDefinitions]
  );

  const onSelect = (data: DropDownRow.IDataItem) => {
    if (data.value === "create-new-item") {
      push(`../${RoutePaths.SelectConnection}`, {
        state: { destinationId: destination.destinationId, currentStep: CreateStepTypes.CREATE_SOURCE },
      });
    } else {
      push(`../${RoutePaths.ConnectionNew}`, {
        state: {
          sourceId: data.value,
          destinationId: destination.destinationId,
          currentStep: CreateStepTypes.CREATE_CONNECTION,
        },
      });
    }

    // const path = `../${RoutePaths.ConnectionNew}`;
    // const state =
    //   data.value === "create-new-item"
    //     ? { destinationId: destination.destinationId }
    //     : {
    //         sourceId: data.value,
    //         destinationId: destination.destinationId,
    //       };

    // push(path, { state });
  };

  const goBack = () => {
    push(`/${RoutePaths.Destination}`);
  };

  const onDelete = async () => {
    await deleteDestination({ connectionsWithDestination, destination });
  };

  // const onCreateClick = () => {
  //   push(`/${RoutePaths.Source}/${RoutePaths.SelectSource}`);
  // };

  const menuItems: CategoryItem[] = pageConfig?.menuConfig || [
    {
      routes: [
        {
          path: RoutePaths.Overview,
          name: <FormattedMessage id="tables.overview" />,
          component: (
            <TableContainer>
              <TableItemTitle
                type="source"
                dropDownData={sourcesDropDownData}
                onSelect={onSelect}
                entityName={destination.name}
                entity={destination.destinationName}
                entityIcon={destinationDefinition.icon ? getIcon(destinationDefinition.icon) : null}
                releaseStage={destinationDefinition.releaseStage}
                // onClick={onCreateClick}
                num={connectionsWithDestination.length}
                btnText={<FormattedMessage id="sources.newSourceTitle" />}
              />
              {connectionsWithDestination.length > 0 && (
                <DestinationConnectionTable connections={connectionsWithDestination} />
              )}
            </TableContainer>
          ),
          show: true,
        },
        {
          path: RoutePaths.Settings,
          name: <FormattedMessage id="tables.settings" />,
          component: (
            <>
              {currentStep === StepsTypes.TEST_CONNECTION && (
                <TestConnection
                  isLoading={loadingStatus}
                  type="destination"
                  onBack={() => {
                    setCurrentStep(StepsTypes.CREATE_ENTITY);
                  }}
                  onFinish={() => {
                    goBack();
                  }}
                />
              )}
              {currentStep === StepsTypes.CREATE_ENTITY && (
                <DestinationSettings
                  currentDestination={destination}
                  errorMessage={fetchingConnectorError}
                  onBack={goBack}
                  formValues={destinationFormValues}
                  afterSubmit={() => {
                    setLoadingStatus(false);
                  }}
                  onShowLoading={(
                    isLoading: boolean,
                    formValues: ServiceFormValues | null,
                    error: JSX.Element | string | null
                  ) => {
                    setDestinationFormValues(formValues);
                    if (isLoading) {
                      setCurrentStep(StepsTypes.TEST_CONNECTION);
                      setLoadingStatus(true);
                    } else {
                      setCurrentStep(StepsTypes.CREATE_ENTITY);
                      setFetchingConnectorError(error);
                    }
                  }}
                />
              )}
            </>
          ),
          show: true,
        },
        {
          path: RoutePaths.DangerZone,
          name: <FormattedMessage id="tables.dangerZone" />,
          component: <DeleteBlock type="destination" onDelete={onDelete} />,
          show: true,
        },
      ],
    },
  ];

  const onSelectMenuItem = (newPath: string) => {
    push(newPath);
  };
  const firstRoute = (): string => {
    const { routes } = menuItems[0];
    const filteredRoutes = routes.filter((route) => route.show === true);
    if (filteredRoutes.length > 0) {
      return filteredRoutes[0]?.path;
    }
    return "";
  };

  return (
    <Container>
      <Breadcrumbs data={breadcrumbsData} currentStep={0} />
      <ConnectorDocumentationWrapper>
        <DefinitioDetails name={destinationDefinition.name} icon={destinationDefinition.icon} type="destination" />
        <TabContainer>
          <TabMenu data={menuItems} onSelect={onSelectMenuItem} activeItem={pathname} size="16" lastOne />
        </TabContainer>
        <ApiErrorBoundary>
          <Suspense fallback={<LoadingPage />}>
            <Routes>
              {menuItems
                .flatMap((menuItem) => menuItem.routes)
                .map(
                  ({ path, component: Component, show }) => show && <Route key={path} path={path} element={Component} />
                )}
              <Route path="*" element={<Navigate to={firstRoute()} replace />} />
            </Routes>
          </Suspense>
        </ApiErrorBoundary>
      </ConnectorDocumentationWrapper>
    </Container>
  );
};

export default DestinationItemPage;

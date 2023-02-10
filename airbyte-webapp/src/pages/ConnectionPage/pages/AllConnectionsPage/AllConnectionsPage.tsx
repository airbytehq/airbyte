import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, LoadingPage, MainPageWithScroll, PageTitle, DropDown, DropDownRow } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import { Pagination } from "components/Pagination";
import { Separator } from "components/Separator";

import { FilterConnectionRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useFilteredConnectionList } from "hooks/services/useConnectionHook";
import { useDestinationOptionList } from "hooks/services/useDestinationHook";
import { useSourceOptionList } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import { RoutePaths } from "../../../routePaths";
import ConnectionsTable from "./components/ConnectionsTable";

const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 4px;
`;

const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
`;

const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  color: #ffffff;
`;

const DDsContainer = styled.div`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 32px;
`;

const DDContainer = styled.div<{
  margin?: string;
}>`
  width: 216px;
  margin: ${({ margin }) => margin};
`;

const Footer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const workspace = useCurrentWorkspace();

  const sourceOptions = useSourceOptionList();
  const destinationOptions = useDestinationOptionList();
  const statusOptions: DropDownRow.IDataItem[] = [
    { label: "All Status", value: "" },
    { label: "Active", value: "active" },
    { label: "Inactive", value: "inactive" },
  ];

  const [filters, setFilters] = useState<FilterConnectionRequestBody>({
    workspaceId: workspace.workspaceId,
    pageSize: 10,
    pageCurrent: 1,
    status: statusOptions[0].value,
    sourceId: sourceOptions[0].value,
    destinationId: destinationOptions[0].value,
  });

  const { connections, total, pageSize } = useFilteredConnectionList(filters);

  const onSelectFilter = (
    filterType: "pageCurrent" | "status" | "sourceId" | "destinationId",
    filterValue: number | string
  ) => {
    setFilters({ ...filters, [filterType]: filterValue });
  };

  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);

  const onCreateClick = () => push(`${RoutePaths.ConnectionNew}`);

  return (
    <Suspense fallback={<LoadingPage />}>
      {connections.length ? (
        <MainPageWithScroll
          withPadding
          headTitle={<HeadTitle titles={[{ title: "Connections" }]} />}
          pageTitle={
            <PageTitle
              title=""
              endComponent={
                <Button onClick={onCreateClick} disabled={!allowCreateConnection} size="m">
                  <BtnInnerContainer>
                    <BtnIcon icon={faPlus} />
                    <BtnText>
                      <FormattedMessage id="connection.newConnection" />
                    </BtnText>
                  </BtnInnerContainer>
                </Button>
              }
            />
          }
        >
          <Separator />
          <DDsContainer>
            <DDContainer margin="0 24px 0 0">
              <DropDown
                $withBorder
                $background="white"
                value={filters.status}
                options={statusOptions}
                onChange={(option: DropDownRow.IDataItem) => onSelectFilter("status", option.value)}
              />
            </DDContainer>
            <DDContainer margin="0 24px 0 0">
              <DropDown
                $withBorder
                $background="white"
                value={filters.sourceId}
                options={sourceOptions}
                onChange={(option: DropDownRow.IDataItem) => onSelectFilter("sourceId", option.value)}
              />
            </DDContainer>
            <DDContainer>
              <DropDown
                $withBorder
                $background="white"
                value={filters.destinationId}
                options={destinationOptions}
                onChange={(option: DropDownRow.IDataItem) => onSelectFilter("destinationId", option.value)}
              />
            </DDContainer>
          </DDsContainer>
          <Separator height="24px" />
          <ConnectionsTable connections={connections} />
          <Separator height="54px" />
          <Footer>
            <Pagination pages={total / pageSize} onChange={(value: number) => onSelectFilter("pageCurrent", value)} />
          </Footer>
        </MainPageWithScroll>
      ) : (
        <EmptyResourceListView
          resourceType="connections"
          onCreateClick={onCreateClick}
          disableCreateButton={!allowCreateConnection}
        />
      )}
    </Suspense>
  );
};

export default AllConnectionsPage;

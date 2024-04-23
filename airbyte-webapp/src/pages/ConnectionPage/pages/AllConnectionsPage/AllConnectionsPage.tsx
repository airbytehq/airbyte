import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Box } from "@mui/material";
import _ from "lodash";
import React, { Suspense, useCallback, useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation, useSearchParams } from "react-router-dom";
import styled from "styled-components";

import { Button, LoadingPage, NewMainPageWithScroll, PageTitle, DropDown, DropDownRow } from "components";
import MessageBox from "components/base/MessageBox";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import { PageSize } from "components/PageSize";
import { Pagination } from "components/Pagination";
import { Separator } from "components/Separator";

import { useUser } from "core/AuthContext";
import { FilterConnectionRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useFilteredConnectionList, useConnectionFilterOptions } from "hooks/services/useConnectionHook";
import { usePageConfig } from "hooks/services/usePageConfig";
import useRouter from "hooks/useRouter";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import NewConnectionsTable from "./components/NewConnectionsTable";
import { RoutePaths } from "../../../routePaths";

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
  // const CONNECTION_PAGE_SIZE = 10;
  const { push, pathname, query } = useRouter();
  const { user, setUser } = useUser();
  const [searchParams] = useSearchParams();
  const authService = useAuthenticationService();
  const token = searchParams.get("token");
  const location = useLocation();
  // const { push, pathname, query } = useRouter();
  const [messageId, setMessageId] = useState<string | undefined>("");
  const [pageConfig, updatePageSize] = usePageConfig();
  const [currentPageSize, setCurrentPageSize] = useState<number>(pageConfig.connection.pageSize);
  const [sortFieldName, setSortFieldName] = useState("");
  const [sortDirection, setSortDirection] = useState("");
  const [localSortOrder, setLocalSortOrder] = useState("");
  const [connectorSortOrder, setConnectorSortOrder] = useState("");
  const [entitySortOrder, setEntitySortOrder] = useState("");
  const [statusSortOrder, setStatusSortOrder] = useState("");
  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const workspace = useCurrentWorkspace();
  const { statusOptions, sourceOptions, destinationOptions } = useConnectionFilterOptions(workspace.workspaceId);

  const initialFiltersState = {
    workspaceId: workspace.workspaceId,
    pageSize: query.pageSize ? JSON.parse(query.pageSize) : pageConfig.connection.pageSize,
    pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
    status: statusOptions[0].value,
    sourceDefinitionId: sourceOptions[0].value,
    destinationDefinitionId: destinationOptions[0].value,
    sortDetails: {
      sortFieldName: query.sortBy ?? sortFieldName,
      sortDirection: query.order ?? sortDirection,
    },
  };

  const [filters, setFilters] = useState<FilterConnectionRequestBody>(initialFiltersState);

  const { connections, total, pageSize } = useFilteredConnectionList(filters);

  const getUserInfo = useCallback(() => {
    if (user?.token !== token) {
      authService
        .getUserInfo(token as string)
        .then((res: any) => {
          setUser?.({ ...res.data, token });
        })
        .catch((err) => {
          if (err.message) {
            console.log(err?.message);
          }
        });
    }
  }, [authService, setUser, token]);

  useEffect(() => {
    if (token) {
      getUserInfo();
    }
  }, []);
  // const connectionIds = connections?.map((con: any) => con?.connectionId);
  // const apiData = {
  //   connectionIds,
  // };

  // const { connectionStatusList } = useConnectionStatusList(apiData) || [];

  // const onSelectFilter = useCallback(
  //   (
  //     filterType: "pageCurrent" | "status" | "sourceDefinitionId" | "destinationDefinitionId" | "pageSize",
  //     filterValue: number | string
  //   ) => {
  //     if (
  //       filterType === "status" ||
  //       filterType === "sourceDefinitionId" ||
  //       filterType === "destinationDefinitionId" ||
  //       filterType === "pageSize"
  //     ) {
  //       setFilters({ ...filters, [filterType]: filterValue, pageCurrent: 1 });
  //     } else if (filterType === "pageCurrent") {
  //       setFilters({ ...filters, [filterType]: filterValue as number });
  //     }
  //   },
  //   [filters]
  // );

  const onSelectFilter = useCallback(
    (
      filterType:
        | "pageCurrent"
        | "status"
        | "sourceDefinitionId"
        | "destinationDefinitionId"
        | "pageSize"
        | "sortDirection"
        | "sortFieldName",
      filterValue: number | string,
      query?: any
    ) => {
      setFilters((prevFilters: any) => {
        if (
          filterType === "destinationDefinitionId" ||
          filterType === "pageSize" ||
          filterType === "status" ||
          filterType === "sourceDefinitionId"
        ) {
          return { ...prevFilters, [filterType]: filterValue };
        } else if (filterType === "sortDirection" || filterType === "sortFieldName") {
          return {
            ...prevFilters,
            sortDetails: {
              ...prevFilters.sortDetails,
              [filterType]: filterValue,
            },
            pageCurrent: prevFilters.pageCurrent,
          };
        } else if (filterType === "pageCurrent") {
          const querySortBy = query?.sortBy ?? "";
          if (querySortBy === "name") {
            setLocalSortOrder(query?.order ?? "");
            setConnectorSortOrder("");
            setStatusSortOrder("");
            setEntitySortOrder("");
          } else if (querySortBy === "connectorName") {
            setConnectorSortOrder(query?.order ?? "");
            setLocalSortOrder("");
            setStatusSortOrder("");
            setEntitySortOrder("");
          } else if (querySortBy === "entityName") {
            setEntitySortOrder(query?.order ?? "");
            setLocalSortOrder("");
            setStatusSortOrder("");
            setConnectorSortOrder("");
          } else if (querySortBy === "status") {
            setStatusSortOrder(query?.order ?? "");
            setLocalSortOrder("");
            setConnectorSortOrder("");
            setEntitySortOrder("");
          } else {
            setEntitySortOrder("");
            setStatusSortOrder("");
            setConnectorSortOrder("");
            setLocalSortOrder("");
          }

          const sortOrder = querySortBy
            ? { sortFieldName: querySortBy, sortDirection: query?.order }
            : { sortFieldName: "", sortDirection: "" };

          return {
            ...prevFilters,
            [filterType]: filterValue,
            sortDetails: sortOrder,
          };
        }
        return prevFilters;
      });
    },
    []
  );

  const hasConnections = useCallback((): boolean => {
    if (_.isEqual(initialFiltersState, filters) && total === 0) {
      return false;
    }
    return true;
  }, [filters, total]);

  const onChangePageSize = useCallback(
    (size: number) => {
      setCurrentPageSize(size);
      updatePageSize("connection", size);
      onSelectFilter("pageSize", size, query);
    },
    [onSelectFilter]
  );
  useEffect(() => {
    if (hasConnections()) {
      const queryParams = new URLSearchParams(location.search);

      // Add or update the sortBy, order, and pageCurrent parameters
      queryParams.set("sortBy", query.sortBy ?? "");
      queryParams.set("order", query.order ?? "");
      queryParams.set("pageCurrent", `${filters.pageCurrent}`);
      queryParams.set("pageSize", `${filters.pageSize}`);

      // Preserve existing query parameters
      const existingParams = new URLSearchParams(location.search);
      existingParams.forEach((value, key) => {
        if (key !== "sortBy" && key !== "order" && key !== "pageCurrent" && key !== "pageSize") {
          queryParams.set(key, value);
        }
      });
      // Update the URL with the new parameters
      push({
        pathname,
        search: queryParams.toString(),
      });
    }
  }, [filters.pageCurrent, filters.pageSize]);

  // useEffect(() => {
  //   if (hasConnections()) {
  //     push({ pathname, search: `?pageCurrent=${filters.pageCurrent}` });
  //   }
  // }, [filters.pageCurrent]);

  useEffect(() => {
    if (Object.keys(query).length > 2 && query?.pageCurrent !== undefined && query?.pageSize !== undefined) {
      setFilters({
        ...filters,
        pageCurrent: JSON.parse(query.pageCurrent),
        pageSize: JSON.parse(query.pageSize),
        sortDetails: {
          sortDirection: query.order,
          sortFieldName: query.sortBy,
        },
      });
    }
  }, [query]);

  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);

  const onCreateClick = () => push(`${RoutePaths.SelectConnection}`);
  const onSetMessageId = (id: string) => setMessageId(id);

  return (
    <Suspense fallback={<LoadingPage position="relative" />}>
      {hasConnections() ? (
        <>
          <MessageBox message={messageId} onClose={() => setMessageId("")} type="info" position="center" />
          <NewMainPageWithScroll
            headTitle={<HeadTitle titles={[{ id: "connection.pageTitle" }]} />}
            pageTitle={
              <PageTitle
                withPadding
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
            <DDsContainer>
              <DDContainer margin="0 24px 0 0">
                <DropDown
                  $withBorder
                  $background="white"
                  value={filters.status}
                  options={statusOptions}
                  onChange={(option: DropDownRow.IDataItem) => onSelectFilter("status", option.value, query)}
                />
              </DDContainer>
              <DDContainer margin="0 24px 0 0">
                <DropDown
                  $withBorder
                  $background="white"
                  value={filters.sourceDefinitionId}
                  options={sourceOptions}
                  onChange={(option: DropDownRow.IDataItem) =>
                    onSelectFilter("sourceDefinitionId", option.value, query)
                  }
                />
              </DDContainer>
              <DDContainer>
                <DropDown
                  $withBorder
                  $background="white"
                  value={filters.destinationDefinitionId}
                  options={destinationOptions}
                  onChange={(option: DropDownRow.IDataItem) =>
                    onSelectFilter("destinationDefinitionId", option.value, query)
                  }
                />
              </DDContainer>
            </DDsContainer>

            <Separator height="10px" />

            <NewConnectionsTable
              connections={connections as any}
              onSetMessageId={onSetMessageId}
              setSortDirection={setSortDirection}
              setSortFieldName={setSortFieldName}
              onSelectFilter={onSelectFilter}
              localSortOrder={localSortOrder}
              setLocalSortOrder={setLocalSortOrder}
              connectorSortOrder={connectorSortOrder}
              setConnectorSortOrder={setConnectorSortOrder}
              entitySortOrder={entitySortOrder}
              setEntitySortOrder={setEntitySortOrder}
              statusSortOrder={statusSortOrder}
              setStatusSortOrder={setStatusSortOrder}
              pageCurrent={filters.pageCurrent}
              pageSize={filters.pageSize}
              // connectionStatus={connectionStatusList as any}
            />
            <Separator height="24px" />
            <Footer>
              <PageSize currentPageSize={currentPageSize} totalPage={total / pageSize} onChange={onChangePageSize} />
              <Box paddingLeft="20px">
                <Pagination
                  pages={total / pageSize}
                  value={filters.pageCurrent}
                  onChange={(value: number) => onSelectFilter("pageCurrent", value, query)}
                />
              </Box>
            </Footer>
            <Separator height="24px" />
          </NewMainPageWithScroll>
        </>
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

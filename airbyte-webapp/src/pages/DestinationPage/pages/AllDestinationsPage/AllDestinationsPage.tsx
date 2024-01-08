import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Box } from "@mui/material";
import _ from "lodash";
import { useState, useCallback, useEffect } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation, useNavigate } from "react-router-dom";
import styled from "styled-components";

import { Button, DropDown, DropDownRow, NewMainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";
import { PageSize } from "components/PageSize";
import PageTitle from "components/PageTitle";
import { Pagination } from "components/Pagination";
import { Separator } from "components/Separator";

//  import queryString from "query-string";
// import { FilterConnectionRequestBody } from "core/request/DaspireClient";
import { FilterDestinationRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
// import { useConnectionFilterOptions, useFilteredConnectionList } from "hooks/services/useConnectionHook";
import { useConnectionFilterOptions } from "hooks/services/useConnectionHook";
import { usePaginatedDestination } from "hooks/services/useDestinationHook";
import { usePageConfig } from "hooks/services/usePageConfig";
import useRouter from "hooks/useRouter";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import DestinationsTable from "./components/DestinationsTable";
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
const Footer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;
const DDContainer = styled.div<{
  margin?: string;
}>`
  width: 195px;
  margin: ${({ margin }) => margin};
  margin-left: auto;
  margin-right: 32px;
`;

const AllDestinationsPage: React.FC = () => {
  const { push, query, pathname } = useRouter();
  const location = useLocation();
  const navigate = useNavigate();

  // const { push } = useRouter();
  // const { destinations } = useDestinationList();

  const [pageConfig, updatePageSize] = usePageConfig();
  // const [pageConfig] = usePageConfig();

  // const [currentPageSize] = useState<number>(pageConfig.connection.pageSize);
  const [pageCurrent, setCurrentPageSize] = useState<number>(pageConfig?.destination?.pageSize);
  const [sortFieldName, setSortFieldName] = useState("");
  const [sortDirection, setSortDirection] = useState("");
  const [localSortOrder, setLocalSortOrder] = useState("");
  const [destinationSortOrder, setDestinationSortOrder] = useState("");

  useTrackPage(PageTrackingCodes.DESTINATION_LIST);
  const workspace = useCurrentWorkspace();
  const { destinationOptions } = useConnectionFilterOptions(workspace?.workspaceId);
  const initialFiltersState = {
    workspaceId: workspace.workspaceId,
    pageSize: query.pageSize ? JSON.parse(query.pageSize) : pageConfig?.destination?.pageSize,
    pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
    DestinationDefinitionId: destinationOptions[0].value,
    sortDetails: {
      sortFieldName,
      sortDirection,
    },
  };

  const [filters, setFilters] = useState<FilterDestinationRequestBody>(initialFiltersState);
  const { destinations, total, pageSize } = usePaginatedDestination(filters);
  // const { destinations, total, pageSize,pageCurrent:paginatedPageCurrent } = usePaginatedDestination(filters);
  // const workspace = useCurrentWorkspace();
  // const { statusOptions, sourceOptions, destinationOptions } = useConnectionFilterOptions();

  // const initialFiltersState = {
  //   workspaceId: workspace.workspaceId,
  //   pageSize: currentPageSize,
  //   pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
  //   status: statusOptions[0].value,
  //   sourceDefinitionId: sourceOptions[0].value,
  //   destinationDefinitionId: destinationOptions[0].value,
  // };

  // const [filters] = useState<FilterConnectionRequestBody>(initialFiltersState);
  // const [filters, setFilters] = useState<FilterConnectionRequestBody>(initialFiltersState);
  // const { connections, total, pageSize } = useFilteredConnectionList(filters);
  // const { connections } = useFilteredConnectionList(filters);
  // const onSelectFilter = useCallback(
  //   (filterType: "pageCurrent" | "DestinationDefinitionId" | "pageSize", filterValue: number | string) => {
  //     if (filterType === "DestinationDefinitionId" || filterType === "pageSize") {
  //       setFilters({ ...filters, [filterType]: filterValue, pageCurrent: 1 });
  //     } else if (filterType === "pageCurrent") {
  //       setFilters({ ...filters, [filterType]: filterValue as number });
  //     }
  //   },
  //   [filters]
  // );
  const onSelectFilter = useCallback(
    (
      filterType: "pageCurrent" | "DestinationDefinitionId" | "pageSize" | "sortDirection" | "sortFieldName",
      filterValue: number | string,
      query: any
    ) => {
      setFilters((prevFilters: any) => {
        if (filterType === "DestinationDefinitionId" || filterType === "pageSize") {
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
            // console.log("1");
            setLocalSortOrder(query?.order ?? "");
            setDestinationSortOrder("");
          } else if (querySortBy === "destinationName") {
            // console.log("2 hello");
            setDestinationSortOrder(query?.order ?? "");
            setLocalSortOrder("");
          } else {
            // console.log("3");
            setLocalSortOrder("");
            setDestinationSortOrder("");
          }

          const sortOrder = querySortBy
            ? { sortFieldName: querySortBy, sortDirection: query?.order }
            : { sortFieldName: "", sortDirection: "" };
          // const newSearchParams: {
          //   pageCurrent?: number | string;
          //   order?: string;
          //   sortBy?: string;
          // } = {
          //   pageCurrent:paginatedPageCurrent,
          //   order: sortOrder.sortDirection ,
          //   sortBy: sortOrder.sortFieldName
          // };
          // push({
          //   search: queryString.stringify(newSearchParams, { skipNull: true }),
          // });
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
  const hasDestination = useCallback((): boolean => {
    if (_.isEqual(initialFiltersState, filters) && total === 0) {
      return false;
    }
    return true;
  }, [filters, total]);
  useEffect(() => {
    if (hasDestination()) {
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
  const onChangePageSize = useCallback(
    (size: number) => {
      setCurrentPageSize(size);
      updatePageSize("destination", size);
      onSelectFilter("pageSize", size, query);
    },
    [onSelectFilter]
  );
  const onCreateDestination = () => push(`${RoutePaths.SelectDestination}`);

  return (
    <>
      {destinations && destinations?.length > 0 ? (
        <NewMainPageWithScroll
          headTitle={<HeadTitle titles={[{ id: "admin.destinations" }]} />}
          pageTitle={
            <PageTitle
              withPadding
              title=""
              endComponent={
                <Button onClick={onCreateDestination} data-id="new-destination">
                  <BtnInnerContainer>
                    <BtnIcon icon={faPlus} />
                    <BtnText>
                      <FormattedMessage id="destinations.newDestination" />
                    </BtnText>
                  </BtnInnerContainer>
                </Button>
              }
            />
          }
        >
          <DDContainer>
            <DropDown
              $withBorder
              $background="white"
              value={filters.DestinationDefinitionId}
              options={destinationOptions}
              onChange={(option: DropDownRow.IDataItem) =>
                onSelectFilter("DestinationDefinitionId", option.value, query)
              }
            />
          </DDContainer>
          <Separator height="10px" />
          <DestinationsTable
            destinations={destinations}
            setSortFieldName={setSortFieldName}
            setSortDirection={setSortDirection}
            onSelectFilter={onSelectFilter}
            localSortOrder={localSortOrder}
            setLocalSortOrder={setLocalSortOrder}
            destinationSortOrder={destinationSortOrder}
            setDestinationSortOrder={setDestinationSortOrder}
            pageCurrent={filters.pageCurrent}
            pageSize={filters.pageSize}
          />
          <Separator height="24px" />
          <Footer>
            <PageSize currentPageSize={pageCurrent} totalPage={total / pageSize} onChange={onChangePageSize} />
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
      ) : (
        navigate(`${RoutePaths.SelectDestination}`)
      )}
    </>
  );
};

export default AllDestinationsPage;

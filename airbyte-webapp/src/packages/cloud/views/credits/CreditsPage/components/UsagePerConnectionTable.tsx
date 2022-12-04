import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import { CellProps } from "react-table";
import styled from "styled-components";

import { SortOrderEnum } from "components/EntityTable/types";
import { Table, SortableTableHeader } from "components/ui/Table";

import { useQuery } from "hooks/useQuery";
import { CreditConsumptionByConnector } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import ConnectionCell from "./ConnectionCell";
import UsageCell from "./UsageCell";

const Content = styled.div`
  padding: 0 60px 0 15px;
`;

const UsageValue = styled.div`
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  padding-right: 10px;
  min-width: 53px;
`;

interface UsagePerConnectionTableProps {
  creditConsumption: CreditConsumptionByConnector[];
}

type FullTableProps = CreditConsumptionByConnector & {
  creditsConsumedPercent: number;
  sourceIcon: string;
  destinationIcon: string;
};

const UsagePerConnectionTable: React.FC<UsagePerConnectionTableProps> = ({ creditConsumption }) => {
  const query = useQuery<{ sortBy?: string; order?: SortOrderEnum }>();
  const navigate = useNavigate();
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const creditConsumptionWithPercent = React.useMemo(() => {
    const sumCreditsConsumed = creditConsumption.reduce((a, b) => a + b.creditsConsumed, 0);
    return creditConsumption.map((item) => {
      const currentSourceDefinition = sourceDefinitions.find(
        (def) => def.sourceDefinitionId === item.sourceDefinitionId
      );
      const currentDestinationDefinition = destinationDefinitions.find(
        (def) => def.destinationDefinitionId === item.destinationDefinitionId
      );

      return {
        ...item,
        sourceIcon: currentSourceDefinition?.icon,
        destinationIcon: currentDestinationDefinition?.icon,
        creditsConsumedPercent: sumCreditsConsumed ? (item.creditsConsumed / sumCreditsConsumed) * 100 : 0,
      };
    });
  }, [creditConsumption, sourceDefinitions, destinationDefinitions]);

  const sortBy = query.sortBy || "connection";
  const sortOrder = query.order || SortOrderEnum.ASC;

  const onSortClick = useCallback(
    (field: string) => {
      const order =
        sortBy !== field ? SortOrderEnum.ASC : sortOrder === SortOrderEnum.ASC ? SortOrderEnum.DESC : SortOrderEnum.ASC;
      navigate({
        search: queryString.stringify(
          {
            sortBy: field,
            order,
          },
          { skipNull: true }
        ),
      });
    },
    [navigate, sortBy, sortOrder]
  );

  const sortData = useCallback(
    (a, b) => {
      const result =
        sortBy === "usage"
          ? a.creditsConsumed - b.creditsConsumed
          : `${a.sourceDefinitionName}${a.destinationDefinitionName}`
              .toLowerCase()
              .localeCompare(`${b.sourceDefinitionName}${b.destinationDefinitionName}`.toLowerCase());

      if (sortOrder === SortOrderEnum.DESC) {
        return -1 * result;
      }

      return result;
    },
    [sortBy, sortOrder]
  );

  const sortingData = React.useMemo(
    () => creditConsumptionWithPercent.sort(sortData),
    [sortData, creditConsumptionWithPercent]
  );

  const columns = React.useMemo(
    () => [
      {
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("connection")}
            isActive={sortBy === "connection"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="credits.connection" />
          </SortableTableHeader>
        ),
        customWidth: 30,
        accessor: "sourceDefinitionName",
        Cell: ({ cell, row }: CellProps<FullTableProps>) => (
          <ConnectionCell
            sourceDefinitionName={cell.value}
            destinationDefinitionName={row.original.destinationDefinitionName}
            sourceIcon={row.original.sourceIcon}
            destinationIcon={row.original.destinationIcon}
          />
        ),
      },
      {
        Header: (
          <SortableTableHeader
            onClick={() => onSortClick("usage")}
            isActive={sortBy === "usage"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="credits.usage" />
          </SortableTableHeader>
        ),
        accessor: "creditsConsumed",
        collapse: true,
        customPadding: { right: 0 },
        Cell: ({ cell }: CellProps<FullTableProps>) => <UsageValue>{cell.value}</UsageValue>,
      },
      {
        Header: "",
        accessor: "creditsConsumedPercent",
        customPadding: { left: 0 },
        Cell: ({ cell }: CellProps<FullTableProps>) => <UsageCell percent={cell.value} />,
      },
      // TODO: Replace to Grow column
      {
        Header: "",
        accessor: "connectionId",
        Cell: <div />,
        customWidth: 20,
      },
    ],
    [onSortClick, sortBy, sortOrder]
  );

  return (
    <Content>
      <Table columns={columns} data={sortingData} light />
    </Content>
  );
};

export default UsagePerConnectionTable;

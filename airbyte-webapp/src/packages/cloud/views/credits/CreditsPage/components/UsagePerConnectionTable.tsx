import { ColumnDef } from "@tanstack/react-table";
import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

import { SortOrderEnum } from "components/EntityTable/types";
import { NextTable } from "components/ui/NextTable";
import { SortableTableHeader } from "components/ui/Table";

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
  sourceIcon?: string;
  destinationIcon?: string;
};

type ColumnDefs = [
  ColumnDef<FullTableProps, string>,
  ColumnDef<FullTableProps, string>,
  ColumnDef<FullTableProps, number>,
  ColumnDef<FullTableProps, string>
];

const UsagePerConnectionTable: React.FC<UsagePerConnectionTableProps> = ({ creditConsumption }) => {
  const query = useQuery<{ sortBy?: string; order?: SortOrderEnum }>();
  const navigate = useNavigate();
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const creditConsumptionWithPercent = React.useMemo<FullTableProps[]>(() => {
    const sumCreditsConsumed = creditConsumption.reduce((a, b) => a + b.creditsConsumed, 0);
    return creditConsumption.map((item) => {
      const currentSourceDefinition = sourceDefinitions.find(
        (def) => def.sourceDefinitionId === item.sourceDefinitionId
      );
      const currentDestinationDefinition = destinationDefinitions.find(
        (def) => def.destinationDefinitionId === item.destinationDefinitionId
      );
      const newItem: FullTableProps = {
        ...item,
        sourceIcon: currentSourceDefinition?.icon,
        destinationIcon: currentDestinationDefinition?.icon,
        creditsConsumedPercent: sumCreditsConsumed ? (item.creditsConsumed / sumCreditsConsumed) * 100 : 0,
      };

      return newItem;
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

  const sortingData = React.useMemo<FullTableProps[]>(
    () => creditConsumptionWithPercent.sort(sortData),
    [sortData, creditConsumptionWithPercent]
  );

  const columns = React.useMemo(
    (): ColumnDefs => [
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("connection")}
            isActive={sortBy === "connection"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="credits.connection" />
          </SortableTableHeader>
        ),
        meta: {
          customWidth: 30,
        },
        accessorKey: "sourceDefinitionName",
        cell: (props) => (
          <ConnectionCell
            sourceDefinitionName={props.cell.getValue()}
            destinationDefinitionName={props.row.original.destinationDefinitionName}
            sourceIcon={props.row.original.sourceIcon}
            destinationIcon={props.row.original.destinationIcon}
          />
        ),
      },
      {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("usage")}
            isActive={sortBy === "usage"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="credits.usage" />
          </SortableTableHeader>
        ),
        accessorKey: "creditsConsumed",
        meta: {
          collapse: true,
          customPadding: {
            right: 0,
          },
        },
        cell: (props) => <UsageValue>{props.cell.getValue()}</UsageValue>,
      },
      {
        header: "",
        accessorKey: "creditsConsumedPercent",
        meta: {
          customPadding: {
            left: 0,
          },
        },
        cell: (props) => <UsageCell percent={props.cell.getValue()} />,
      },
      // TODO: Replace to Grow column
      {
        header: "",
        accessorKey: "connectionId",
        cell: () => <div />,
        meta: {
          customWidth: 20,
        },
      },
    ],
    [onSortClick, sortBy, sortOrder]
  );

  return (
    <Content>
      <NextTable columns={columns} data={sortingData} light />
    </Content>
  );
};

export default UsagePerConnectionTable;

import { createColumnHelper } from "@tanstack/react-table";
import classNames from "classnames";
import queryString from "query-string";
import React, { useCallback } from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useNavigate } from "react-router-dom";

import { SortOrderEnum } from "components/EntityTable/types";
import { NextTable } from "components/ui/NextTable";
import { SortableTableHeader } from "components/ui/Table";
import { Text } from "components/ui/Text";

import { useQuery } from "hooks/useQuery";
import { CreditConsumptionByConnector } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import ConnectionCell from "./ConnectionCell";
import UsageCell from "./UsageCell";
import styles from "./UsagePerConnectionTable.module.scss";

interface UsagePerConnectionTableProps {
  creditConsumption: CreditConsumptionByConnector[];
}

type FullTableProps = CreditConsumptionByConnector & {
  creditsConsumedPercent: number;
  sourceIcon?: string;
  destinationIcon?: string;
};

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

  const sortingData = React.useMemo(
    // This is temporary solution, since there is an issue with array that
    // creditConsumptionWithPercent.sort(sortData) returns; when passed into useReactTable
    // the reference to this array stays the same, so useReactTable is not updating the table,
    // therefore sorting not working; after implementing native react table sorting mechanism
    // this problem should be solved
    () => [...creditConsumptionWithPercent.sort(sortData)],
    [sortData, creditConsumptionWithPercent]
  );

  const columnHelper = createColumnHelper<FullTableProps>();

  const columns = React.useMemo(
    () => [
      columnHelper.accessor("sourceDefinitionName", {
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
          thClassName: classNames(styles.thConnection, styles.light),
        },
        cell: (props) => (
          <ConnectionCell
            sourceDefinitionName={props.cell.getValue()}
            destinationDefinitionName={props.row.original.destinationDefinitionName}
            sourceIcon={props.row.original.sourceIcon}
            destinationIcon={props.row.original.destinationIcon}
          />
        ),
      }),
      columnHelper.accessor("creditsConsumed", {
        header: () => (
          <SortableTableHeader
            onClick={() => onSortClick("usage")}
            isActive={sortBy === "usage"}
            isAscending={sortOrder === SortOrderEnum.ASC}
          >
            <FormattedMessage id="credits.usage" />
          </SortableTableHeader>
        ),
        meta: {
          thClassName: classNames(styles.thCreditsConsumed, styles.light),
        },
        cell: (props) => (
          <Text className={styles.usageValue} size="lg">
            <FormattedNumber value={props.cell.getValue()} maximumFractionDigits={2} minimumFractionDigits={2} />
          </Text>
        ),
      }),
      columnHelper.accessor("creditsConsumedPercent", {
        header: "",
        meta: {
          thClassName: classNames(styles.thCreditsConsumedPercent, styles.light),
        },
        cell: (props) => <UsageCell percent={props.cell.getValue()} />,
      }),
      columnHelper.accessor("connectionId", {
        header: "",
        cell: () => <div />,
        meta: {
          thClassName: classNames(styles.thConnectionId, styles.light),
        },
      }),
    ],
    [columnHelper, onSortClick, sortBy, sortOrder]
  );

  return (
    <div className={styles.content}>
      <NextTable columns={columns} data={sortingData} light />
    </div>
  );
};

export default UsagePerConnectionTable;

import React from "react";
import { DbMigrationInfoItem } from "core/resources/DbMigration";
import { Block } from "../../ConnectorsPage/components/PageComponents";
import Table from "components/Table/Table";
import { FormattedMessage } from "react-intl";

type MigrationsViewProps = {
  migrations: Array<DbMigrationInfoItem>;
};

const defaultSortField = [{ id: "migrationVersion" }];

const MigrationTableView: React.FC<MigrationsViewProps> = ({ migrations }) => {
  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="dbMigration.type" />,
        accessor: "migrationType",
      },
      {
        Header: <FormattedMessage id="dbMigration.version" />,
        accessor: "migrationVersion",
      },
      {
        Header: <FormattedMessage id="dbMigration.description" />,
        accessor: "migrationDescription",
      },
      {
        Header: <FormattedMessage id="dbMigration.state" />,
        accessor: "migrationState",
      },
      {
        Header: <FormattedMessage id="dbMigration.migratedBy" />,
        id: "migratedBy",
        accessor: (row: any) =>
          row.migratedBy === "null" ? "" : row.migratedBy,
      },
      {
        Header: <FormattedMessage id="dbMigration.migratedAt" />,
        id: "migratedAt",
        accessor: (row: any) => new Date(row.migratedAt).toLocaleString(),
      },
      {
        Header: <FormattedMessage id="dbMigration.script" />,
        accessor: "migrationScript",
      },
    ],
    [migrations]
  );

  return (
    <>
      {migrations.length > 0 && (
        <Block>
          <Table
            columns={columns}
            data={migrations}
            sortBy={defaultSortField}
          />
        </Block>
      )}
    </>
  );
};

export default MigrationTableView;

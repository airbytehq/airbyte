import React from "react";
import HeadTitle from "components/HeadTitle";
import { DbMigrationInfoItem } from "core/resources/DbMigration";
import { Block, Title } from "../../ConnectorsPage/components/PageComponents";
import Table from "components/Table/Table";
import { FormattedMessage } from "react-intl";

type MigrationsViewProps = {
  database: string;
  migrations: Array<DbMigrationInfoItem>;
};

const defaultSortField = [{ id: "migrationVersion" }];

const MigrationsView: React.FC<MigrationsViewProps> = ({
  database,
  migrations,
}) => {
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
        accessor: "migratedBy",
      },
      {
        Header: <FormattedMessage id="dbMigration.migratedAt" />,
        accessor: "migratedAt",
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
      <HeadTitle titles={[{ id: "settings.dbMigrations" }]} />
      {migrations.length > 0 && (
        <Block>
          <Title bold>{database} Database Migrations</Title>
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

export default MigrationsView;

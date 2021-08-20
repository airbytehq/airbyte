import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";

import { DbMigrationInfoItem } from "core/resources/DbMigration";
import { LoadingButton } from "components";
import useDbMigration from "components/hooks/services/useDbMigration";

import MigrationTableView from "./MigrationTableView";
import { Block, Title } from "./PageComponents";

type DbMigrationComponentProps = {
  databaseTitle: string;
  databaseIdentifier: string;
};

const MigrationComponent: React.FC<DbMigrationComponentProps> = ({
  databaseTitle,
  databaseIdentifier,
}) => {
  const { info, migrate } = useDbMigration();

  const [migrations, setMigrations] = useState<Array<DbMigrationInfoItem>>([]);
  const [hasPendingMigration, setHasPendingMigration] = useState(false);

  useEffect(() => {
    info(databaseIdentifier).then((result) => setMigrations(result.migrations));
  }, []);

  useEffect(() => {
    const hasPending = migrations.some(
      (migration) => migration.migrationState === "Pending"
    );
    setHasPendingMigration(hasPending);
  }, [migrations]);

  const [{ loading: migrating }, onMigrate] = useAsyncFn(async () => {
    await migrate(databaseIdentifier);
    const result = await info(databaseIdentifier);
    setMigrations(result.migrations);
  }, [migrate]);

  return (
    <>
      <Block>
        <Title bold>
          {databaseTitle} <FormattedMessage id="dbMigration.titleSuffix" />
          <LoadingButton
            onClick={onMigrate}
            isLoading={migrating}
            disabled={!hasPendingMigration}
          >
            <FormattedMessage id="admin.runMigration" />
          </LoadingButton>
        </Title>

        <MigrationTableView migrations={migrations} />
      </Block>
    </>
  );
};

export default MigrationComponent;

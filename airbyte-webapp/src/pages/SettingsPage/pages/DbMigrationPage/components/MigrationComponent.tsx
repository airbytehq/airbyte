import React, { useEffect, useState } from "react";
import { useFetcher } from "rest-hooks";
import DbMigrationResource, {
  DbMigrationInfoItem,
} from "core/resources/DbMigration";
import useDbMigration from "components/hooks/services/useDbMigrationHook";
import { useAsyncFn } from "react-use";
import { Block, Title } from "../../ConnectorsPage/components/PageComponents";
import { LoadingButton } from "components";
import { FormattedMessage } from "react-intl";
import MigrationTableView from "./MigrationTableView";

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

  useEffect(() => {
    info(databaseIdentifier).then((result) => setMigrations(result.migrations));
  }, []);

  const [{ loading: migrating }, onMigrate] = useAsyncFn(async () => {
    await migrate(databaseIdentifier);
    const result = await info(databaseIdentifier);
    setMigrations(result.migrations);
  }, [migrate]);

  useFetcher(DbMigrationResource.infoShape());

  return (
    <>
      <Block>
        <Title bold>
          {databaseTitle} <FormattedMessage id="dbMigration.titleSuffix" />
          <LoadingButton onClick={onMigrate} isLoading={migrating}>
            <FormattedMessage id="admin.runMigration" />
          </LoadingButton>
        </Title>

        <MigrationTableView migrations={migrations} />
      </Block>
    </>
  );
};

export default MigrationComponent;

import React from "react";
import MigrationsView from "./components/MigrationsView";
import { Block } from "../ConnectorsPage/components/PageComponents";
import { useResource } from "rest-hooks";
import DbMigrationResource from "core/resources/DbMigration";

const DbMigrationsPage: React.FC = () => {
  const {
    migrations: configsDbMigrations,
  } = useResource(DbMigrationResource.infoShape(), { database: "configs" });
  const {
    migrations: jobsDbMigrations,
  } = useResource(DbMigrationResource.infoShape(), { database: "jobs" });

  return (
    <>
      <Block>
        <MigrationsView database="Configs" migrations={configsDbMigrations} />
      </Block>
      <Block>
        <MigrationsView database="Jobs" migrations={jobsDbMigrations} />
      </Block>
    </>
  );
};

export default DbMigrationsPage;

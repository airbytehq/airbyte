import React from "react";
import HeadTitle from "components/HeadTitle";
import MigrationComponent from "./components/MigrationComponent";

const DbMigrationsPage: React.FC = () => {
  return (
    <>
      <HeadTitle titles={[{ id: "settings.dbMigrations" }]} />
      <MigrationComponent
        databaseTitle="Configs"
        databaseIdentifier="configs"
      />
      <MigrationComponent databaseTitle="Jobs" databaseIdentifier="jobs" />
    </>
  );
};

export default DbMigrationsPage;

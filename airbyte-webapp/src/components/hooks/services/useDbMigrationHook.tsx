import DbMigrationResource, {
  DbMigrationInfoResult,
  DbMigrationMigrateResult,
} from "core/resources/DbMigration";
import { useAnalytics } from "../useAnalytics";
import { useFetcher } from "rest-hooks";

type DbMigrationService = {
  info: (database: string) => Promise<DbMigrationInfoResult>;
  migrate: (database: string) => Promise<DbMigrationMigrateResult>;
};

const useDbMigration = (): DbMigrationService => {
  const analyticsService = useAnalytics();
  const getMigrationInfo = useFetcher(DbMigrationResource.infoShape());
  const runMigration = useFetcher(DbMigrationResource.migrateShape());

  const info = async (database: string) => {
    return await getMigrationInfo({ database });
  };
  const migrate = async (database: string) => {
    analyticsService.track("Run migration", { database });
    return await runMigration({ database });
  };

  return {
    info,
    migrate,
  };
};

export default useDbMigration;

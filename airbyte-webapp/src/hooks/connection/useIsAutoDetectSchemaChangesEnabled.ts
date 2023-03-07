import { useExperiment } from "hooks/services/Experiment";

const isEnabledInEnv = process.env.REACT_APP_AUTO_DETECT_SCHEMA_CHANGES === "true";

export const useIsAutoDetectSchemaChangesEnabled = () =>
  useExperiment("connection.autoDetectSchemaChanges", isEnabledInEnv);

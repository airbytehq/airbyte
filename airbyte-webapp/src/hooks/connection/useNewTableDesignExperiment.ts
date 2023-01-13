import { useExperiment } from "hooks/services/Experiment";

export const useNewTableDesignExperiment = () =>
  useExperiment("connection.newTableDesign", import.meta.env.REACT_APP_NEW_STREAMS_TABLE === "true");

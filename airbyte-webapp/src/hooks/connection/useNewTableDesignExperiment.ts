import { useExperiment } from "hooks/services/Experiment";

export const useNewTableDesignExperiment = () => useExperiment("connection.newTableDesign", true);

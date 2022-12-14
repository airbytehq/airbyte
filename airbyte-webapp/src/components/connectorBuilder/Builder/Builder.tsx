import { Form } from "formik";
import { useEffect } from "react";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "../types";
import styles from "./Builder.module.scss";
import { BuilderSidebar } from "./BuilderSidebar";
import { GlobalConfigView } from "./GlobalConfigView";
import { StreamConfigView } from "./StreamConfigView";

interface BuilderProps {
  values: BuilderFormValues;
  toggleYamlEditor: () => void;
}

export const Builder: React.FC<BuilderProps> = ({ values, toggleYamlEditor }) => {
  const { setBuilderFormValues, selectedView } = useConnectorBuilderState();
  useEffect(() => {
    setBuilderFormValues(values);
  }, [values, setBuilderFormValues]);

  return (
    <div className={styles.container}>
      <BuilderSidebar className={styles.sidebar} toggleYamlEditor={toggleYamlEditor} />
      <Form className={styles.form}>
        {selectedView === "global" ? <GlobalConfigView /> : <StreamConfigView streamNum={selectedView} />}
      </Form>
    </div>
  );
};

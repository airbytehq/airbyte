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
  console.log("values", values);
  const { setBuilderFormValues, selectedView } = useConnectorBuilderState();
  useEffect(() => {
    console.log("setting builder form values", values);
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

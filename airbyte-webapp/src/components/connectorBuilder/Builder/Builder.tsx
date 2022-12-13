import { Form } from "formik";
import { useEffect } from "react";

import { BuilderView, useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "../types";
import styles from "./Builder.module.scss";
import { BuilderSidebar } from "./BuilderSidebar";
import { GlobalConfigView } from "./GlobalConfigView";
import { InputsView } from "./InputsView";
import { StreamConfigView } from "./StreamConfigView";

interface BuilderProps {
  values: BuilderFormValues;
  toggleYamlEditor: () => void;
}

function getView(selectedView: BuilderView) {
  switch (selectedView) {
    case "global":
      return <GlobalConfigView />;
    case "inputs":
      return <InputsView />;
    default:
      return <StreamConfigView streamNum={selectedView} />;
  }
}

export const Builder: React.FC<BuilderProps> = ({ values, toggleYamlEditor }) => {
  const { setBuilderFormValues, selectedView, builderFormValues } = useConnectorBuilderState();
  console.log(builderFormValues);
  useEffect(() => {
    setBuilderFormValues(values);
  }, [values, setBuilderFormValues]);

  return (
    <div className={styles.container}>
      <BuilderSidebar className={styles.sidebar} toggleYamlEditor={toggleYamlEditor} />
      <Form className={styles.form}>{getView(selectedView)}</Form>
    </div>
  );
};

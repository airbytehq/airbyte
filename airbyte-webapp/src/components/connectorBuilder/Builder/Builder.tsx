import { Form } from "formik";
import { useEffect, useState } from "react";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { usePatchFormik } from "views/Connector/ConnectorForm/useBuildForm";

import styles from "./Builder.module.scss";
import { BuilderSidebar } from "./BuilderSidebar";
import { GlobalConfigView } from "./GlobalConfigView";
import { StreamConfigView } from "./StreamConfigView";
import { BuilderFormValues } from "./types";

export const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

interface BuilderProps {
  values: BuilderFormValues;
  toggleYamlEditor: () => void;
}

export const Builder: React.FC<BuilderProps> = ({ values, toggleYamlEditor }) => {
  const { setBuilderFormValues } = useConnectorBuilderState();
  useEffect(() => {
    setBuilderFormValues(values);
  }, [values, setBuilderFormValues]);

  const [selectedView, setSelectedView] = useState<"global" | number>("global");

  console.log("values", values);

  return (
    <>
      <FormikPatch />
      <div className={styles.container}>
        <BuilderSidebar
          className={styles.sidebar}
          toggleYamlEditor={toggleYamlEditor}
          numStreams={values.streams.length}
          onViewSelect={setSelectedView}
        />
        <Form className={styles.form}>
          {selectedView === "global" ? <GlobalConfigView /> : <StreamConfigView streamNum={selectedView} />}
        </Form>
      </div>
    </>
  );
};

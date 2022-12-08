import { Form } from "formik";
import { useEffect, useState } from "react";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { usePatchFormik } from "views/Connector/ConnectorForm/useBuildForm";

import styles from "./Builder.module.scss";
import { BuilderSidebar, BuilderView } from "./BuilderSidebar";
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
  const { setBuilderFormValues, setSelectedStream } = useConnectorBuilderState();
  // const { setFieldTouched } = useFormikContext();
  useEffect(() => {
    setBuilderFormValues(values);
  }, [values, setBuilderFormValues]);

  const [selectedView, setSelectedView] = useState<BuilderView>("global");

  // const handleConfigViewBlur = () => {

  // }

  const handleViewSelect = (newSelectedView: BuilderView, streamName?: string) => {
    // if (selectedView === "global") {
    //   setFieldTouched("global");
    // } else {
    //   setFieldTouched(`streams[${selectedView}]`);
    // }

    setSelectedView(newSelectedView);
    if (newSelectedView !== "global" && streamName !== undefined) {
      setSelectedStream(streamName);
    }
  };

  return (
    <>
      <FormikPatch />
      <div className={styles.container}>
        <BuilderSidebar
          className={styles.sidebar}
          toggleYamlEditor={toggleYamlEditor}
          numStreams={values.streams.length}
          onViewSelect={handleViewSelect}
          selectedView={selectedView}
        />
        <Form className={styles.form}>
          {selectedView === "global" ? <GlobalConfigView /> : <StreamConfigView streamNum={selectedView} />}
        </Form>
      </div>
    </>
  );
};

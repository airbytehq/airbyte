import { Form } from "formik";
import { useEffect, useState } from "react";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "../types";
import styles from "./Builder.module.scss";
import { BuilderSidebar, BuilderView } from "./BuilderSidebar";
import { GlobalConfigView } from "./GlobalConfigView";
import { StreamConfigView } from "./StreamConfigView";

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
    <div className={styles.container}>
      <BuilderSidebar
        className={styles.sidebar}
        toggleYamlEditor={toggleYamlEditor}
        onViewSelect={handleViewSelect}
        selectedView={selectedView}
      />
      <Form className={styles.form}>
        {selectedView === "global" ? <GlobalConfigView /> : <StreamConfigView streamNum={selectedView} />}
      </Form>
    </div>
  );
};

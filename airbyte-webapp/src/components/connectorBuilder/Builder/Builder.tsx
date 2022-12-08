import { Form } from "formik";
import { useEffect, useState } from "react";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./Builder.module.scss";
import { BuilderSidebar, BuilderView } from "./BuilderSidebar";
import { GlobalConfigView } from "./GlobalConfigView";
import { StreamConfigView } from "./StreamConfigView";
import { BuilderFormValues } from "./types";

interface BuilderProps {
  values: BuilderFormValues;
  toggleYamlEditor: () => void;
}

export const Builder: React.FC<BuilderProps> = ({ values, toggleYamlEditor }) => {
  const { setBuilderFormValues, setSelectedStream } = useConnectorBuilderState();
  useEffect(() => {
    setBuilderFormValues(values);
  }, [values, setBuilderFormValues]);

  const [selectedView, setSelectedView] = useState<BuilderView>("global");

  const handleViewSelect = (selectedView: BuilderView, streamName?: string) => {
    setSelectedView(selectedView);
    if (selectedView !== "global" && streamName !== undefined) {
      setSelectedStream(streamName);
    }
  };

  return (
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
  );
};

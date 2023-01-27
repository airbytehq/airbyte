import { Form } from "formik";
import debounce from "lodash/debounce";
import { useEffect, useMemo } from "react";

import { BuilderView, useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./Builder.module.scss";
import { BuilderSidebar } from "./BuilderSidebar";
import { GlobalConfigView } from "./GlobalConfigView";
import { InputsView } from "./InputsView";
import { StreamConfigView } from "./StreamConfigView";
import { builderFormValidationSchema, BuilderFormValues } from "../types";

interface BuilderProps {
  values: BuilderFormValues;
  validateForm: () => void;
  toggleYamlEditor: () => void;
}

function getView(selectedView: BuilderView, hasMultipleStreams: boolean) {
  switch (selectedView) {
    case "global":
      return <GlobalConfigView />;
    case "inputs":
      return <InputsView />;
    default:
      return <StreamConfigView streamNum={selectedView} hasMultipleStreams={hasMultipleStreams} />;
  }
}

export const Builder: React.FC<BuilderProps> = ({ values, toggleYamlEditor, validateForm }) => {
  const { setBuilderFormValues, selectedView } = useConnectorBuilderFormState();
  const debouncedSetBuilderFormValues = useMemo(
    () =>
      debounce((values) => {
        // kick off formik validation
        validateForm();
        // update upstream state
        setBuilderFormValues(values, builderFormValidationSchema.isValidSync(values));
      }, 200),
    [setBuilderFormValues, validateForm]
  );
  useEffect(() => {
    debouncedSetBuilderFormValues(values);
  }, [values, debouncedSetBuilderFormValues]);

  return (
    <div className={styles.container}>
      <BuilderSidebar className={styles.sidebar} toggleYamlEditor={toggleYamlEditor} />
      <Form className={styles.form}>{getView(selectedView, values.streams.length > 1)}</Form>
    </div>
  );
};

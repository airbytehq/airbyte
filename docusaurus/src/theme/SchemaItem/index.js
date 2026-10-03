import { useState } from "react";
import SchemaItem from "@theme-original/SchemaItem";
import { ConnectorSpecPicker } from "@site/src/components/ConnectorSpecPicker";
import styles from "./styles.module.css";

const CONNECTOR_CONFIGURATION_TITLES = {
  SourceConfiguration: "source",
  DestinationConfiguration: "destination",
};

function ConnectorSpecLookup({ connectorType }) {
  const [open, setOpen] = useState(false);

  return (
    <div className={styles.lookup}>
      <button
        type="button"
        className={styles.toggle}
        onClick={() => setOpen(!open)}
      >
        {open ? "Hide" : "Look up"} {connectorType} configuration fields
      </button>
      {open && <ConnectorSpecPicker connectorType={connectorType} compact />}
    </div>
  );
}

export default function SchemaItemWrapper(props) {
  const connectorType = CONNECTOR_CONFIGURATION_TITLES[props.schema?.title];

  if (!connectorType) {
    return <SchemaItem {...props} />;
  }

  return (
    <SchemaItem {...props}>
      {props.children}
      <ConnectorSpecLookup connectorType={connectorType} />
    </SchemaItem>
  );
}

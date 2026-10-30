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
        className={`button button--primary button--sm ${styles.toggle}`}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        {open ? "Hide" : "Look up"} {connectorType} configuration fields
        <svg
          className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            d="M9 18l6-6-6-6"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </svg>
      </button>
      {open && (
        <div className={styles.panel}>
          <ConnectorSpecPicker connectorType={connectorType} compact />
        </div>
      )}
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

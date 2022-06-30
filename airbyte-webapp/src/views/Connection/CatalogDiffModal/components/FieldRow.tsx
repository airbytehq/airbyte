import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import styles from "./StreamRow.module.scss";

interface StreamRowProps {
  item: StreamTransform;
  catalog: AirbyteCatalog;
}

export const SyncModeBox: React.FC<{ syncModeString: string; mode: "remove" | "update" }> = ({
  syncModeString,
  mode,
}) => {
  const syncModeBoxStyle = classnames(styles.syncModeBox, {
    [styles.remove]: mode === "remove",
  });
  return <div className={syncModeBoxStyle}> {syncModeString} </div>;
};

export const StreamRow: React.FC<StreamRowProps> = ({ item, catalog }) => {
  const diffType = item.transformType.includes("add") ? "remove" : "add";
  const rowStyle = classnames(styles.row, {
    [styles.add]: diffType === "add",
    [styles.remove]: diffType === "remove",
  });

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: diffType === "add",
    [styles.minus]: diffType === "remove",
  });

  const streamConfig = catalog.streams.find(
    (stream) =>
      stream.stream?.namespace === item.streamDescriptor.namespace && stream.stream?.name === item.streamDescriptor.name
  )?.config;

  const syncModeString = `${streamConfig?.syncMode} | ${streamConfig?.destinationSyncMode}`;

  return (
    <div className={rowStyle}>
      {diffType === "add" ? (
        <FontAwesomeIcon icon={faPlus} size="1x" className={iconStyle} />
      ) : (
        <FontAwesomeIcon icon={faMinus} size="1x" className={iconStyle} />
      )}
      <div className={styles.name}>{item.streamDescriptor.name}</div>
      {diffType === "remove" && streamConfig?.selected && <SyncModeBox syncModeString={syncModeString} mode="remove" />}
    </div>
  );
};

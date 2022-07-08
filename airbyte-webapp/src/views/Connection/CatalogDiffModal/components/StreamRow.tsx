import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import { ModificationIcon } from "./ModificationIcon";
import styles from "./StreamRow.module.scss";

interface StreamRowProps {
  item: StreamTransform;
  catalog: AirbyteCatalog;
}

export const SyncModeBox: React.FC<{ syncModeString: string }> = ({ syncModeString }) => {
  return <div className={styles.syncModeBox}> {syncModeString} </div>;
};

export const StreamRow: React.FC<StreamRowProps> = ({ item, catalog }) => {
  const diffType = item.transformType.includes("add")
    ? "add"
    : item.transformType.includes("remove")
    ? "remove"
    : "update";

  const rowStyle = classnames(styles.row, {
    [styles.add]: diffType === "add",
    [styles.remove]: diffType === "remove",
  });

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: diffType === "add",
    [styles.minus]: diffType === "remove",
    [styles.mod]: diffType === "update",
  });

  // These properties may or may not exist on any given stream

  const streamConfig = catalog.streams.find(
    (stream) =>
      stream.stream?.namespace === item.streamDescriptor.namespace && stream.stream?.name === item.streamDescriptor.name
  )?.config;
  const syncModeString = `${streamConfig?.syncMode} | ${streamConfig?.destinationSyncMode}`;
  const itemName = item.streamDescriptor.name;
  const namespace = item.streamDescriptor.namespace;

  return (
    <tr className={rowStyle}>
      <td>
        {diffType === "add" ? (
          <FontAwesomeIcon icon={faPlus} size="1x" className={iconStyle} />
        ) : diffType === "remove" ? (
          <FontAwesomeIcon icon={faMinus} size="1x" className={iconStyle} />
        ) : (
          <ModificationIcon />
        )}
      </td>
      {namespace && <td className={styles.nameCell}>{namespace}</td>}
      <td className={styles.nameCell}>{itemName}</td>
      {diffType === "remove" && streamConfig?.selected && syncModeString && (
        <td>
          <SyncModeBox syncModeString={syncModeString} />
        </td>
      )}
    </tr>
  );
};

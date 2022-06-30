import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { AirbyteCatalog, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

import { ModificationIcon } from "./ModificationIcon";
import styles from "./StreamRow.module.scss";

interface StreamRowProps {
  item: StreamTransform | FieldTransform;
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
  // if it's a stream, get the catalog data
  // if it's a field, get the field type

  // render the row!
  // use the transformType to use classnames to apply condiitonal styling

  // const itemType = item.transformType.includes("stream") ? "stream" : "field";

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

  let syncModeString = null;
  let streamConfig = null;
  let namespace = null;
  // const fieldType = null;

  let itemName = "";

  if ("streamDescriptor" in item) {
    streamConfig = catalog.streams.find(
      (stream) =>
        stream.stream?.namespace === item.streamDescriptor.namespace &&
        stream.stream?.name === item.streamDescriptor.name
    )?.config;
    syncModeString = `${streamConfig?.syncMode} | ${streamConfig?.destinationSyncMode}`;
    itemName = item.streamDescriptor.name;
    namespace = item.streamDescriptor.namespace;
  } else if ("fieldName" in item) {
    itemName = item.fieldName[item.fieldName.length - 1];
    // fieldType = item.updateFieldSchema?.newSchema;
  }

  return (
    <tr className={rowStyle}>
      {diffType === "add" ? (
        <FontAwesomeIcon icon={faPlus} size="1x" className={iconStyle} />
      ) : diffType === "remove" ? (
        <FontAwesomeIcon icon={faMinus} size="1x" className={iconStyle} />
      ) : (
        <ModificationIcon />
      )}
      {namespace && <td className={styles.nameCell}>{namespace}</td>}
      <td className={styles.nameCell}>{itemName}</td>
      {syncModeString && streamConfig && streamConfig?.selected && (
        <td>
          <SyncModeBox syncModeString={syncModeString} mode="remove" />
        </td>
      )}
    </tr>
  );
};

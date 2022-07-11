import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { StreamTransform } from "core/request/AirbyteClient";

import { useCatalogContext } from "../CatalogContext";
import { ModificationIcon } from "./ModificationIcon";
import styles from "./StreamRow.module.scss";

interface StreamRowProps {
  stream: StreamTransform;
}

export const SyncModeBox: React.FC<{ syncModeString: string }> = ({ syncModeString }) => {
  return <div className={styles.syncModeBox}> {syncModeString} </div>;
};

export const StreamRow: React.FC<StreamRowProps> = ({ stream }) => {
  const { catalog } = useCatalogContext();

  const diffType = stream.transformType.includes("add")
    ? "add"
    : stream.transformType.includes("remove")
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

  console.log(catalog.streams);

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const streamConfig = catalog!.streams.find(
    (stream) =>
      stream.stream?.namespace === stream.streamDescriptor.namespace &&
      stream.stream?.name === stream.streamDescriptor.name
  )?.config;

  const syncModeString = `${streamConfig?.syncMode} | ${streamConfig?.destinationSyncMode}`;
  const itemName = stream.streamDescriptor.name;
  const namespace = stream.streamDescriptor.namespace;

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

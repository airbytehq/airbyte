import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { ModificationIcon } from "components/icons/ModificationIcon";

import { StreamTransform } from "core/request/AirbyteClient";

import styles from "./StreamRow.module.scss";
import { DiffVerb } from "./types";

interface StreamRowProps {
  streamTransform: StreamTransform;
  syncMode?: string;

  diffVerb: DiffVerb;
}

export const SyncModeBox: React.FC<{ syncModeString: string }> = ({ syncModeString }) => {
  return <div className={styles.syncModeBox}> {syncModeString} </div>;
};

export const StreamRow: React.FC<StreamRowProps> = ({ streamTransform, syncMode, diffVerb }) => {
  const rowStyle = classnames(styles.row, {
    [styles.add]: diffVerb === "new",
    [styles.remove]: diffVerb === "removed",
  });

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: diffVerb === "new",
    [styles.minus]: diffVerb === "removed",
    [styles.mod]: diffVerb === "changed",
  });

  const itemName = streamTransform.streamDescriptor.name;
  const namespace = streamTransform.streamDescriptor.namespace;
  const hasSyncModeChange = diffVerb === "removed" && syncMode;

  return (
    <tr className={rowStyle}>
      <td className={styles.nameCell}>
        <div className={styles.content}>
          <div className={styles.iconContainer}>
            {diffVerb === "new" ? (
              <FontAwesomeIcon icon={faPlus} size="1x" className={iconStyle} />
            ) : diffVerb === "removed" ? (
              <FontAwesomeIcon icon={faMinus} size="1x" className={iconStyle} />
            ) : (
              <ModificationIcon />
            )}
          </div>
          <div title={namespace} className={styles.text}>
            {namespace}
          </div>
        </div>
      </td>
      <td
        className={classnames(styles.nameCell, { [styles.lg]: !hasSyncModeChange })}
        colSpan={hasSyncModeChange ? 1 : 2}
      >
        <div title={itemName} className={styles.text}>
          {itemName}
        </div>
      </td>
      {hasSyncModeChange && (
        <td>
          <SyncModeBox syncModeString={syncMode} />
        </td>
      )}
    </tr>
  );
};

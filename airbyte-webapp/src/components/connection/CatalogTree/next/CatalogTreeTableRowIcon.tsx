import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { ModificationIcon } from "components/icons/ModificationIcon";

import { SyncSchemaStream } from "core/domain/catalog";

import styles from "./CatalogTreeTableRowIcon.module.scss";
import { useCatalogTreeTableRowProps } from "./useCatalogTreeTableRowProps";

interface CatalogTreeTableRowIconProps {
  stream: SyncSchemaStream;
}
export const CatalogTreeTableRowIcon: React.FC<CatalogTreeTableRowIconProps> = ({ stream }) => {
  const { statusToDisplay, isSelected } = useCatalogTreeTableRowProps(stream);

  if (statusToDisplay === "added") {
    return (
      <FontAwesomeIcon
        icon={faPlus}
        size="2x"
        className={classNames(styles.icon, { [styles.plus]: !isSelected, [styles.changed]: isSelected })}
      />
    );
  } else if (statusToDisplay === "removed") {
    return (
      <FontAwesomeIcon
        icon={faMinus}
        size="2x"
        className={classNames(styles.icon, { [styles.minus]: !isSelected, [styles.changed]: isSelected })}
      />
    );
  } else if (statusToDisplay === "changed") {
    return (
      <div className={classNames(styles.icon, styles.changed)}>
        <ModificationIcon color={styles.modificationIconColor} />
      </div>
    );
  }
  return <div />;
};

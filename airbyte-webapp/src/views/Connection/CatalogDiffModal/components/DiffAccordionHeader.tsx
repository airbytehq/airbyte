import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import { useIntl } from "react-intl";

import { ModificationIcon } from "components/icons/ModificationIcon";

import { StreamDescriptor } from "core/request/AirbyteClient";

import styles from "./DiffAccordionHeader.module.scss";
import { DiffIconBlock } from "./DiffIconBlock";

interface DiffAccordionHeaderProps {
  open: boolean;

  streamDescriptor: StreamDescriptor;
  removedCount: number;
  newCount: number;
  changedCount: number;
}
export const DiffAccordionHeader: React.FC<DiffAccordionHeaderProps> = ({
  open,
  streamDescriptor,
  removedCount,
  newCount,
  changedCount,
}) => {
  // eslint-disable-next-line css-modules/no-undef-class
  const nameCellStyle = classnames(styles.nameCell, styles.row);

  // eslint-disable-next-line css-modules/no-undef-class
  const namespaceCellStyles = classnames(styles.nameCell, styles.row, styles.namespace);

  const { formatMessage } = useIntl();

  return (
    <>
      <ModificationIcon />
      <div className={namespaceCellStyles} aria-labelledby={formatMessage({ id: "connection.updateSchema.namespace" })}>
        {open ? <FontAwesomeIcon icon={faAngleDown} /> : <FontAwesomeIcon icon={faAngleRight} />}
        <div className={styles.headerAdjust}>{streamDescriptor.namespace}</div>
      </div>
      <div className={nameCellStyle} aria-labelledby={formatMessage({ id: "connection.updateSchema.streamName" })}>
        <div className={styles.headerAdjust}>{streamDescriptor.name}</div>
      </div>
      <DiffIconBlock removedCount={removedCount} newCount={newCount} changedCount={changedCount} />
    </>
  );
};

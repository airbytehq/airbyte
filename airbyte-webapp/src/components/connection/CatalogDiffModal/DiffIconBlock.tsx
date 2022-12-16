import { useIntl } from "react-intl";

import { NumberBadge } from "components/ui/NumberBadge";

import styles from "./DiffIconBlock.module.scss";

interface DiffIconBlockProps {
  newCount: number;
  removedCount: number;
  changedCount: number;
}
export const DiffIconBlock: React.FC<DiffIconBlockProps> = ({ newCount, removedCount, changedCount }) => {
  const { formatMessage } = useIntl();

  return (
    <div className={styles.iconBlock}>
      {removedCount > 0 && (
        <NumberBadge
          value={removedCount}
          color="red"
          aria-label={`${formatMessage(
            {
              id: "connection.updateSchema.removed",
            },
            {
              value: removedCount,
              item: formatMessage({ id: "connection.updateSchema.field" }, { count: removedCount }),
            }
          )}`}
        />
      )}
      {newCount > 0 && (
        <NumberBadge
          value={newCount}
          color="green"
          aria-label={`${formatMessage(
            {
              id: "connection.updateSchema.new",
            },
            {
              value: newCount,
              item: formatMessage({ id: "connection.updateSchema.field" }, { count: newCount }),
            }
          )}`}
        />
      )}
      {changedCount > 0 && (
        <NumberBadge
          value={changedCount}
          color="blue"
          aria-label={`${formatMessage(
            {
              id: "connection.updateSchema.changed",
            },
            {
              value: changedCount,
              item: formatMessage({ id: "connection.updateSchema.field" }, { count: changedCount }),
            }
          )}`}
        />
      )}
    </div>
  );
};

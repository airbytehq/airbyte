import classNames from "classnames";
import React from "react";
import { FormattedRelativeTime } from "react-intl";

import { Text } from "components/ui/Text";

import styles from "./LastSyncCell.module.scss";

interface LastSyncCellProps {
  timeInSeconds?: number | null;
  enabled?: boolean;
}

export const LastSyncCell: React.FC<LastSyncCellProps> = ({ timeInSeconds, enabled }) => {
  return (
    <>
      {timeInSeconds ? (
        <Text className={classNames(styles.text, { [styles.enabled]: enabled })} size="sm">
          <FormattedRelativeTime value={timeInSeconds - Date.now() / 1000} updateIntervalInSeconds={60} />
        </Text>
      ) : null}
    </>
  );
};

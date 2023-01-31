import classNames from "classnames";
import React from "react";
import { FormattedRelativeTime } from "react-intl";

import { Text } from "components/ui/Text";

import styles from "./LastSyncCell.module.scss";

interface LastSyncCellProps {
  timeInSecond: number;
  enabled?: boolean;
}

export const LastSyncCell: React.FC<LastSyncCellProps> = ({ timeInSecond, enabled }) => {
  return (
    <>
      {timeInSecond ? (
        <Text className={classNames(styles.text, { [styles.enabled]: enabled })} size="sm">
          <FormattedRelativeTime value={timeInSecond - Date.now() / 1000} updateIntervalInSeconds={60} />
        </Text>
      ) : null}
    </>
  );
};

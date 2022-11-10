import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { DropDownOptionDataItem } from "components/ui/DropDown";
import { PillSelect } from "components/ui/PillSelect";

import { DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";

import styles from "./SyncModeSelect.module.scss";

interface SyncModeValue {
  syncMode: SyncMode;
  destinationSyncMode: DestinationSyncMode;
}

interface SyncModeOption {
  value: SyncModeValue;
}

interface SyncModeSelectProps {
  options: SyncModeOption[];
  value: Partial<SyncModeValue>;
  onChange?: (option: DropDownOptionDataItem<SyncModeValue>) => void;
}

export const SyncModeSelect: React.FC<SyncModeSelectProps> = ({ options, onChange, value }) => {
  const pillSelectOptions = useMemo(() => {
    return options.map(({ value }) => {
      const { syncMode, destinationSyncMode } = value;
      return {
        label: (
          <>
            <FormattedMessage id={`syncMode.${syncMode}`} />
            {` | `}
            <FormattedMessage id={`destinationSyncMode.${destinationSyncMode}`} />
          </>
        ),
        value,
      };
    });
  }, [options]);

  return <PillSelect options={pillSelectOptions} value={value} onChange={onChange} className={styles.pillSelect} />;
};

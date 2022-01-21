import React from "react";
import { SyncSettingsDropdown } from "views/Connection/CatalogTree/components/SyncSettingsCell";
import { SUPPORTED_MODES } from "./formConfig";

const DefaultSyncSettingsField: React.FC<{}> = () => {
  const onChange = (value: any) => {
    console.log(value);
  };

  return (
    <SyncSettingsDropdown
      options={SUPPORTED_MODES.map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      }))}
      onChange={onChange}
    />
  );
};

export { DefaultSyncSettingsField };

import { useLocalStorage } from "react-use";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";

type SettingsByWorkspace = Record<string, boolean>;

export const useAdvancedModeSetting = (): [boolean, (newSetting: boolean) => void] => {
  const { workspaceId } = useCurrentWorkspace();
  const [advancedModeSettingsByWorkspace, setAdvancedModeSettingsByWorkspace] = useLocalStorage<SettingsByWorkspace>(
    "advancedMode",
    {}
  );

  const isAdvancedMode = (advancedModeSettingsByWorkspace || {})[workspaceId] ?? false;
  const setAdvancedMode = (newSetting: boolean) =>
    setAdvancedModeSettingsByWorkspace({ ...advancedModeSettingsByWorkspace, [workspaceId]: newSetting });

  return [isAdvancedMode, setAdvancedMode];
};

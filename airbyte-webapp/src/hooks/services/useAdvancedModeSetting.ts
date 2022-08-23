import { useLocalStorage } from "react-use";

type SettingsByWorkspace = Record<string, boolean>;

export const useAdvancedModeSetting = (workspaceId: string): [boolean, (newSetting: boolean) => void] => {
  const [advancedModeSettingsByWorkspace, setAdvancedModeSettingsByWorkspace] = useLocalStorage<SettingsByWorkspace>(
    "advancedMode",
    {}
  );

  const isAdvancedMode = (advancedModeSettingsByWorkspace || {})[workspaceId] ?? false;
  const setAdvancedMode = (newSetting: boolean) =>
    setAdvancedModeSettingsByWorkspace({ ...advancedModeSettingsByWorkspace, ...{ [workspaceId]: newSetting } });

  return [isAdvancedMode, setAdvancedMode];
};

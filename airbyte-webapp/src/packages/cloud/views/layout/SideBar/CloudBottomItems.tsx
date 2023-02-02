import { FormattedMessage } from "react-intl";

import { CreditsIcon } from "components/icons/CreditsIcon";

import { FeatureItem, useFeature } from "hooks/services/Feature";
import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { RoutePaths } from "pages/routePaths";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { MenuContent } from "views/layout/SideBar/components/MenuContent";
import { NavItem } from "views/layout/SideBar/components/NavItem";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";

import { CloudResourcesDropdown } from "./CloudResourcesDropdown";
import { CloudSupportDropdown } from "./CloudSupportDropdown";
import { LOW_BALANCE_CREDIT_THRESHOLD } from "../../credits/CreditsPage/components/LowCreditBalanceHint/LowCreditBalanceHint";

export const CloudBottomItems: React.FC = () => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const isAllowUpdateConnectorsEnabled = useFeature(FeatureItem.AllowUpdateConnectors);

  return (
    <ul>
      <MenuContent>
        <li>
          <NavItem
            as="navLink"
            to={CloudRoutes.Credits}
            icon={<CreditsIcon />}
            label={<FormattedMessage id="sidebar.credits" />}
            testId="creditsButton"
            withNotification={cloudWorkspace.remainingCredits <= LOW_BALANCE_CREDIT_THRESHOLD}
          />
        </li>
        <li>
          <CloudResourcesDropdown />
        </li>
        <li>
          <CloudSupportDropdown />
        </li>
        <li>
          <NavItem
            as="navLink"
            label={<FormattedMessage id="sidebar.settings" />}
            icon={<SettingsIcon />}
            to={RoutePaths.Settings}
            withNotification={isAllowUpdateConnectorsEnabled}
          />
        </li>
      </MenuContent>
    </ul>
  );
};

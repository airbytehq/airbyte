import { FormattedMessage, useIntl } from "react-intl";

import Link from "components/Link";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { useExperiment } from "hooks/services/Experiment";
import {
  InviteUsersModalServiceProvider,
  useInviteUsersModalService,
} from "packages/cloud/services/users/InviteUsersModalService";
import { CloudSettingsRoutes } from "packages/cloud/views/settings/routePaths";
import { RoutePaths } from "pages/routePaths";

import styles from "./InviteUsersHint.module.scss";
import { InviteUsersHintProps } from "./types";

const ACCESS_MANAGEMENT_PATH = `../../${RoutePaths.Settings}/${CloudSettingsRoutes.AccessManagement}`;

const InviteUsersHintContent: React.VFC<InviteUsersHintProps> = ({ connectorType }) => {
  const { formatMessage } = useIntl();
  const { toggleInviteUsersModalOpen } = useInviteUsersModalService();
  const linkToUsersPage = useExperiment("connector.inviteUserHint.linkToUsersPage", false);

  const inviteUsersCta = linkToUsersPage ? (
    <Link to={ACCESS_MANAGEMENT_PATH} target="_blank" rel="noreferrer">
      <FormattedMessage id="inviteUsersHint.cta" />
    </Link>
  ) : (
    <Button
      variant="secondary"
      onClick={() => {
        toggleInviteUsersModalOpen();
      }}
    >
      <FormattedMessage id="inviteUsersHint.cta" />
    </Button>
  );

  return (
    <div className={styles.container}>
      <Text size="sm">
        <FormattedMessage
          id="inviteUsersHint.message"
          values={{
            connector: formatMessage({ id: `connector.${connectorType}` }).toLowerCase(),
          }}
        />
      </Text>
      {inviteUsersCta}
    </div>
  );
};

export const InviteUsersHint: React.VFC<InviteUsersHintProps> = (props) => {
  const isVisible = !useExperiment("connector.inviteUserHint.visible", false);

  return isVisible ? (
    <InviteUsersModalServiceProvider>
      <InviteUsersHintContent {...props} />
    </InviteUsersModalServiceProvider>
  ) : null;
};

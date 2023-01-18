import classNames from "classnames";
import { FormattedMessage, useIntl } from "react-intl";

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

const ACCESS_MANAGEMENT_PATH = `../${RoutePaths.Settings}/${CloudSettingsRoutes.AccessManagement}`;

const InviteUsersHintContent: React.VFC<InviteUsersHintProps> = ({ connectorType }) => {
  const { formatMessage } = useIntl();
  const { toggleInviteUsersModalOpen } = useInviteUsersModalService();
  const linkToUsersPage = useExperiment("connector.inviteUsersHint.linkToUsersPage", false);

  const inviteUsersCta = linkToUsersPage ? (
    <a href={ACCESS_MANAGEMENT_PATH} target="_blank" rel="noreferrer" data-testid="inviteUsersHint-cta">
      <FormattedMessage id="inviteUsersHint.cta" />
    </a>
  ) : (
    <Button
      className={styles.ctaButton}
      variant="secondary"
      data-testid="inviteUsersHint-cta"
      onClick={() => {
        toggleInviteUsersModalOpen();
      }}
    >
      <FormattedMessage id="inviteUsersHint.cta" />
    </Button>
  );

  return (
    <Text
      size="sm"
      className={classNames(styles.container, linkToUsersPage && styles.withLink)}
      data-testid="inviteUsersHint"
    >
      <FormattedMessage
        id="inviteUsersHint.message"
        values={{
          connector: formatMessage({ id: `connector.${connectorType}` }).toLowerCase(),
        }}
      />{" "}
      {inviteUsersCta}
    </Text>
  );
};

export const InviteUsersHint: React.VFC<InviteUsersHintProps> = (props) => {
  const isVisible = useExperiment("connector.inviteUsersHint.visible", false);

  return isVisible ? (
    <InviteUsersModalServiceProvider invitedFrom={props.connectorType}>
      <InviteUsersHintContent {...props} />
    </InviteUsersModalServiceProvider>
  ) : null;
};

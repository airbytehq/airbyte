import { FormattedMessage, useIntl } from "react-intl";

import Button from "components/base/Button";

import {
  InviteUsersModalServiceProvider,
  useInviteUsersModalService,
} from "packages/cloud/services/users/InviteUsersModalService";

import styles from "./InviteUsersHint.module.scss";

interface InviteUsersHintProps {
  connectorType: "source" | "destination";
}

const InviteUsersHintContent: React.VFC<InviteUsersHintProps> = ({ connectorType }) => {
  const { formatMessage } = useIntl();
  const { toggleInviteUsersModalOpen } = useInviteUsersModalService();

  const onCtaClick: React.MouseEventHandler<HTMLButtonElement> = () => {
    toggleInviteUsersModalOpen();
  };

  return (
    <div className={styles.container}>
      <FormattedMessage
        id="inviteUsersHint.message"
        values={{
          connector: formatMessage({ id: `connector.${connectorType}` }).toLowerCase(),
        }}
      />
      <Button secondary onClick={onCtaClick}>
        <FormattedMessage id="inviteUsersHint.cta" />
      </Button>
    </div>
  );
};

export const InviteUsersHint: React.VFC<InviteUsersHintProps> = (props) => (
  <InviteUsersModalServiceProvider>
    <InviteUsersHintContent {...props} />
  </InviteUsersModalServiceProvider>
);

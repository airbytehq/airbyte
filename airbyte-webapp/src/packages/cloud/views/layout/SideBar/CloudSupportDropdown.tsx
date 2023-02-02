import { faCircleQuestion, faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage, useIntl } from "react-intl";
import { useIntercom } from "react-use-intercom";

import { DropdownMenuOptionType } from "components/ui/DropdownMenu";

import { links } from "utils/links";
import ChatIcon from "views/layout/SideBar/components/ChatIcon";
import { NavDropdown } from "views/layout/SideBar/components/NavDropdown";

export const CloudSupportDropdown: React.FC = () => {
  const { formatMessage } = useIntl();
  const { show } = useIntercom();
  const handleChatUs = (data: DropdownMenuOptionType) => data.value === "chatUs" && show();

  return (
    <NavDropdown
      options={[
        {
          as: "a",
          href: links.supportTicketLink,
          icon: <FontAwesomeIcon icon={faEnvelope} />,
          displayName: formatMessage({ id: "sidebar.supportTicket" }),
        },
        {
          as: "button",
          value: "chatUs",
          icon: <ChatIcon />,
          displayName: formatMessage({ id: "sidebar.chat" }),
        },
      ]}
      onChange={handleChatUs}
      label={<FormattedMessage id="sidebar.support" />}
      icon={<FontAwesomeIcon icon={faCircleQuestion} size="2x" />}
    />
  );
};

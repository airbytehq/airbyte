import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faDesktop } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage, useIntl } from "react-intl";

import { DocsIcon } from "components/icons/DocsIcon";

import { links } from "utils/links";
import { NavDropdown } from "views/layout/SideBar/components/NavDropdown";
import StatusIcon from "views/layout/SideBar/components/StatusIcon";

export const CloudResourcesDropdown: React.FC = () => {
  const { formatMessage } = useIntl();
  return (
    <NavDropdown
      options={[
        {
          as: "a",
          href: links.docsLink,
          icon: <DocsIcon />,
          displayName: formatMessage({ id: "sidebar.documentation" }),
        },
        {
          as: "a",
          href: links.slackLink,
          icon: <FontAwesomeIcon icon={faSlack} />,
          displayName: formatMessage({ id: "sidebar.joinSlack" }),
        },
        {
          as: "a",
          href: links.statusLink,
          icon: <StatusIcon />,
          displayName: formatMessage({ id: "sidebar.status" }),
        },
        {
          as: "a",
          href: links.demoLink,
          icon: <FontAwesomeIcon icon={faDesktop} />,
          displayName: formatMessage({ id: "sidebar.demo" }),
        },
      ]}
      label={<FormattedMessage id="sidebar.resources" />}
      icon={<DocsIcon />}
    />
  );
};

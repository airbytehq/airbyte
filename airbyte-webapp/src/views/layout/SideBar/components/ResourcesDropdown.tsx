import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage, useIntl } from "react-intl";

import { DocsIcon } from "components/icons/DocsIcon";

import { links } from "utils/links";

import { NavDropdown } from "./NavDropdown";
import RecipesIcon from "./RecipesIcon";

export const ResourcesDropdown: React.FC = () => {
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
          href: links.tutorialLink,
          icon: <RecipesIcon />,
          displayName: formatMessage({ id: "sidebar.recipes" }),
        },
      ]}
      label={<FormattedMessage id="sidebar.resources" />}
      icon={<DocsIcon />}
    />
  );
};

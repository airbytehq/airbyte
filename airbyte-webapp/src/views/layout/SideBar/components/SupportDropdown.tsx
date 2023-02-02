import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage, useIntl } from "react-intl";

import { DocsIcon } from "components/icons/DocsIcon";
import { DropdownMenu } from "components/ui/DropdownMenu";
import { Text } from "components/ui/Text";

import { links } from "utils/links";

import RecipesIcon from "./RecipesIcon";

export const SupportDropdown: React.FC = () => {
  const { formatMessage } = useIntl();
  return (
    <DropdownMenu
      placement="right"
      displacement={10}
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
    >
      {({ open }) => (
        <button className={classNames(styles.dropdownMenuButton, { [styles.open]: open })}>
          <DocsIcon />
          <Text className={styles.text} size="sm">
            <FormattedMessage id="sidebar.resources" />
          </Text>
        </button>
      )}
    </DropdownMenu>
  );
};

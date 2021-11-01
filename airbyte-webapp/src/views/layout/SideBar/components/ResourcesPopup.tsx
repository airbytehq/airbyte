import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSlack } from "@fortawesome/free-brands-svg-icons";

import { useConfig } from "config";
import { Popout } from "components";
import DocsIcon from "./DocsIcon";
import RecipesIcon from "./RecipesIcon";
import StatusIcon from "./StatusIcon";

const Item = styled.a`
  display: flex;
  flex-direction: row;
  align-items: center;
  text-decoration: none;
  color: ${({ theme }) => theme.textColor};
  font-size: 14px;
  font-weight: 500;
`;

const Icon = styled.div`
  width: 34px;
  font-size: 22px;
`;

const ResourcesPopup: React.FC<{
  children: (props: { onOpen: () => void }) => React.ReactNode;
}> = ({ children }) => {
  const config = useConfig();

  const options = [
    {
      value: "docs",
      label: (
        <Item href={config.ui.docsLink} target="_blank">
          <Icon>
            <DocsIcon />
          </Icon>
          <FormattedMessage id="sidebar.documentation" />
        </Item>
      ),
    },
    {
      value: "slack",
      label: (
        <Item href={config.ui.slackLink} target="_blank">
          <Icon>
            {/*@ts-ignore slack icon fails here*/}
            <FontAwesomeIcon icon={faSlack} />
          </Icon>
          <FormattedMessage id="sidebar.joinSlack" />
        </Item>
      ),
    },
    {
      value: "status",
      label: (
        <Item href={config.ui.statusLink} target="_blank">
          <Icon>
            <StatusIcon />
          </Icon>
          <FormattedMessage id="sidebar.status" />
        </Item>
      ),
    },
    {
      value: "recipes",
      label: (
        <Item href={config.ui.recipesLink} target="_blank">
          <Icon>
            <RecipesIcon />
          </Icon>
          <FormattedMessage id="sidebar.recipes" />
        </Item>
      ),
    },
  ];

  return (
    <Popout
      targetComponent={(targetProps) =>
        children({ onOpen: targetProps.onOpen })
      }
      isSearchable={false}
      options={options}
    />
  );
};

export default ResourcesPopup;

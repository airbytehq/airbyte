import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Popout } from "components";

import { useConfig } from "config";

import DocsIcon from "./DocsIcon";
import RecipesIcon from "./RecipesIcon";
import StatusIcon from "./StatusIcon";

export const Item = styled.a`
  display: flex;
  flex-direction: row;
  align-items: center;
  text-decoration: none;
  color: ${({ theme }) => theme.textColor};
  font-size: 14px;
  font-weight: 500;
`;

export const Icon = styled.div`
  width: 34px;
  font-size: 22px;
`;

const SidebarPopout: React.FC<{
  children: (props: { onOpen: () => void }) => React.ReactNode;
  options: Array<{ value: string; label?: React.ReactNode }>;
}> = ({ children, options }) => {
  const config = useConfig();

  const listData = useMemo(
    () =>
      options.map((item) => {
        switch (item.value) {
          case "docs":
            return {
              value: "docs",
              label: (
                <Item href={config.links.docsLink} target="_blank">
                  <Icon>
                    <DocsIcon />
                  </Icon>
                  <FormattedMessage id="sidebar.documentation" />
                </Item>
              ),
            };
          case "slack":
            return {
              value: "slack",
              label: (
                <Item href={config.links.slackLink} target="_blank">
                  <Icon>
                    <FontAwesomeIcon icon={faSlack} />
                  </Icon>
                  <FormattedMessage id="sidebar.joinSlack" />
                </Item>
              ),
            };
          case "status":
            return {
              value: "status",
              label: (
                <Item href={config.links.statusLink} target="_blank">
                  <Icon>
                    <StatusIcon />
                  </Icon>
                  <FormattedMessage id="sidebar.status" />
                </Item>
              ),
            };
          case "recipes":
            return {
              value: "recipes",
              label: (
                <Item href={config.links.recipesLink} target="_blank">
                  <Icon>
                    <RecipesIcon />
                  </Icon>
                  <FormattedMessage id="sidebar.recipes" />
                </Item>
              ),
            };
          case "ticket":
            return {
              value: "ticket",
              label: (
                <Item href={config.links.supportTicketLink} target="_blank">
                  <Icon>
                    <FontAwesomeIcon icon={faEnvelope} />
                  </Icon>
                  <FormattedMessage id="sidebar.supportTicket" />
                </Item>
              ),
            };
          default:
            return {
              value: item.value,
              label: item.label ?? item.value,
            };
        }
      }),
    [options, config]
  );

  return (
    <Popout
      targetComponent={(targetProps) => children({ onOpen: targetProps.onOpen })}
      styles={{
        menuPortal: (base) => ({
          ...base,
          // TODO: temporary dirty hack
          transform: "translate3D(100px, -100px, 0px)",
        }),
      }}
      isSearchable={false}
      options={listData}
    />
  );
};

export default SidebarPopout;

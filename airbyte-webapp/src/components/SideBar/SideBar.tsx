import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLifeRing, faBook, faCog } from "@fortawesome/free-solid-svg-icons";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";

import Link from "../Link";
import Source from "./components/Source";
import Destination from "./components/Destination";
import { Routes } from "../../pages/routes";
import config from "../../config";

const Bar = styled.nav`
  width: 100px;
  min-width: 65px;
  height: 100%;
  background: ${({ theme }) => theme.darkPrimaryColor};
  padding: 9px 3px 23px 4px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

const Menu = styled.ul`
  padding: 0;
  margin: 10px 0 0;
  width: 100%;
`;

const MenuItem = styled(NavLink)`
  color: ${({ theme }) => theme.greyColor30};
  width: 100%;
  cursor: pointer;
  border-radius: 4px;
  height: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-weight: normal;
  font-size: 12px;
  line-height: 15px;
  margin-top: 7px;
  text-decoration: none;

  &.active {
    color: ${({ theme }) => theme.whiteColor};
    background: ${({ theme }) => theme.primaryColor};
  }
`;

const MenuLinkItem = styled.a`
  color: ${({ theme }) => theme.greyColor30};
  width: 100%;
  cursor: pointer;
  height: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-weight: normal;
  font-size: 12px;
  line-height: 15px;
  margin-top: 7px;
  text-decoration: none;
`;

const Text = styled.div`
  margin-top: 7px;
`;

const DocsIcon = styled(FontAwesomeIcon)`
  font-size: 18px;
  line-height: 18px;
`;

const HelpIcon = styled(FontAwesomeIcon)`
  font-size: 21px;
  line-height: 21px;
`;

const AdminIcon = styled(FontAwesomeIcon)`
  font-size: 15px;
  line-height: 15px;
`;

const SideBar: React.FC = () => {
  return (
    <Bar>
      <div>
        <Link to={Routes.Root}>
          <img src="/simpleLogo.svg" alt="logo" height={50} width={50} />
        </Link>
        <Menu>
          <li>
            <MenuItem
              to={Routes.Root}
              exact
              activeClassName="active"
              isActive={(_, location) =>
                location.pathname === Routes.Root ||
                location.pathname.startsWith(Routes.Source)
              }
            >
              <Source />
              <Text>
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={Routes.Destination} activeClassName="active">
              <Destination />
              <Text>
                <FormattedMessage id="sidebar.destination" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={Routes.Admin} activeClassName="active">
              <AdminIcon icon={faCog} />
              <Text>
                <FormattedMessage id="sidebar.admin" />
              </Text>
            </MenuItem>
          </li>
        </Menu>
      </div>
      <Menu>
        <li>
          <MenuLinkItem href={config.ui.helpLink} target="_blank">
            <HelpIcon icon={faLifeRing} />
            <Text>
              <FormattedMessage id="sidebar.help" />
            </Text>
          </MenuLinkItem>
        </li>
        <li>
          <MenuLinkItem href={config.ui.docsLink} target="_blank">
            <DocsIcon icon={faBook} />
            <Text>
              <FormattedMessage id="sidebar.docs" />
            </Text>
          </MenuLinkItem>
        </li>
      </Menu>
    </Bar>
  );
};

export default SideBar;

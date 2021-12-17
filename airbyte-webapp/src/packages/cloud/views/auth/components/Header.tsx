import React from "react";
import styled from "styled-components";
import { Link } from "react-router-dom";
import { FormattedMessage } from "react-intl";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";

import { Button } from "components";
import { CloudRoutes } from "../../../cloudRoutes";

const Links = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

const BackLink = styled.div`
  font-style: normal;
  font-weight: bold;
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.primaryColor};
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
`;

const FormLink = styled.div`
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.darkGreyColor};
`;

const TextBlock = styled.div`
  padding: 0 9px;
  display: inline-block;
`;

type HeaderProps = {
  toLogin?: boolean;
};

const Header: React.FC<HeaderProps> = ({ toLogin }) => {
  return (
    <Links>
      <BackLink>
        <FontAwesomeIcon icon={faArrowLeft} />
        <TextBlock>Back</TextBlock>
      </BackLink>
      <FormLink>
        <TextBlock>
          <FormattedMessage
            id={toLogin ? "login.haveAccount" : "login.DontHaveAccount"}
          />
        </TextBlock>
        <Button
          secondary
          as={Link}
          to={toLogin ? CloudRoutes.Login : CloudRoutes.Signup}
        >
          <FormattedMessage id={toLogin ? "login.login" : "login.signup"} />
        </Button>
      </FormLink>
    </Links>
  );
};

export default Header;

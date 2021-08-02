import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

import { H2, H4, H5 } from "components";
import NewsItem from "./NewsItem";
import { FormattedMessage } from "react-intl";
import config from "config";

const Icon = styled.img`
  height: 214px;
  margin: 0 auto 21px;
  display: block;
`;

const GitBlock = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 17px;
`;

const GitIcon = styled(FontAwesomeIcon)`
  margin-right: 10px;
  font-size: 36px;
`;

const GitLink = styled.a`
  text-decoration: none;
  color: ${({ theme }) => theme.textColor};
`;

const News: React.FC = () => {
  return (
    <>
      <div>
        <Icon src="/cloud/hello.png" width={184} />
        <NewsItem />
        <NewsItem />
        <NewsItem />
      </div>
      <GitLink href={config.ui.gitLink} target="_blank">
        <H2>
          <FormattedMessage id="login.selfhosting" />
        </H2>
        <GitBlock>
          {/*@ts-ignore github icon fails here*/}
          <GitIcon icon={faGithub} />
          <div>
            <H4>
              <FormattedMessage id="login.opensource" />
            </H4>
            <H5>
              <FormattedMessage id="login.deployInfrastructure" />
            </H5>
          </div>
        </GitBlock>
      </GitLink>
    </>
  );
};

export default News;

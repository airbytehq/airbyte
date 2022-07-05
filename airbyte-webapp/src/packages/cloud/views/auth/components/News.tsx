import { faGithub } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H2, H4, H5 } from "components";

import { useConfig } from "config";
import { news } from "packages/cloud/data/news";

import NewsItem from "./NewsItem";

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

const NewsItemStyled = styled(NewsItem)`
  margin-bottom: 12px;
`;

const News: React.FC = () => {
  const config = useConfig();
  return (
    <>
      <div>
        <Icon src="/cloud-hello.png" width={184} />
        {news.map((n, i) => (
          <NewsItemStyled key={i} {...n} />
        ))}
      </div>
      <GitLink href={config.links.gitLink} target="_blank">
        <H2>
          <FormattedMessage id="login.selfhosting" />
        </H2>
        <GitBlock>
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

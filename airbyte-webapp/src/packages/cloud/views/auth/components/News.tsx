import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

import NewsItem from "./NewsItem";
import { H2, H3, H4 } from "../../../components/Titles";

const Icon = styled.div`
  width: 184px;
  height: 214px;
  margin: 0 auto 21px;
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

const News: React.FC = () => {
  return (
    <>
      <div>
        <Icon>Icon</Icon>
        <NewsItem />
        <NewsItem />
        <NewsItem />
      </div>
      <div>
        <H2>Interested in self-hosting?</H2>
        <GitBlock>
          {/*@ts-ignore github icon fails here*/}
          <GitIcon icon={faGithub} />
          <div>
            <H3>Open-source</H3>
            <H4>Deploy in your own infrastructure. Free forever. </H4>
          </div>
        </GitBlock>
      </div>
    </>
  );
};

export default News;

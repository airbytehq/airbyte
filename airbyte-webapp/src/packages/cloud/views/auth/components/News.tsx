import React from "react";
import styled from "styled-components";

import { news } from "packages/cloud/data/news";

import NewsItem from "./NewsItem";

const Icon = styled.img`
  height: 214px;
  margin: 0 auto 21px;
  display: block;
`;

const NewsItemStyled = styled(NewsItem)`
  margin-bottom: 12px;
`;
// TBD This component possibly is obsolete
const News: React.FC = () => {
  return (
    <div>
      <Icon src="/cloud-hello.png" width={184} />
      {news.map((n, i) => (
        <NewsItemStyled key={i} {...n} />
      ))}
    </div>
  );
};

export default News;

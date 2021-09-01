import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

import ContentCard from "../ContentCard";
import { ConnectionBlockItem } from "./components/ConnectionBlockItem";

type IProps = {
  className?: string;
  itemFrom?: { name: string; icon?: string };
  itemTo?: { name: string; icon?: string };
};

const LightContentCard = styled(ContentCard)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  padding: 20px 21px 19px;
  margin-bottom: 12px;
`;

const Arrow = styled(FontAwesomeIcon)`
  font-size: 29px;
  line-height: 29px;
  color: ${({ theme }) => theme.primaryColor};
`;

const ExtraBlock = styled.div`
  width: 257px;
`;

const ConnectionBlock: React.FC<IProps> = (props) => (
  <LightContentCard className={props.className}>
    {props.itemFrom ? (
      <ConnectionBlockItem {...props.itemFrom} />
    ) : (
      <ExtraBlock />
    )}
    <Arrow icon={faChevronRight} />
    {props.itemTo ? <ConnectionBlockItem {...props.itemTo} /> : <ExtraBlock />}
  </LightContentCard>
);

export default ConnectionBlock;

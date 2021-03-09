import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

import ContentCard from "../ContentCard";
import Item from "./components/Item";

type IProps = {
  className?: string;
  itemFrom?: { name: string; img?: string };
  itemTo?: { name: string; img?: string };
};

const LightContentCard = styled(ContentCard)`
  background: ${({ theme }) => theme.backgroundColor};
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
    {props.itemFrom ? <Item {...props.itemFrom} /> : <ExtraBlock />}
    <Arrow icon={faChevronRight} />
    {props.itemTo ? <Item {...props.itemTo} /> : <ExtraBlock />}
  </LightContentCard>
);

export default ConnectionBlock;

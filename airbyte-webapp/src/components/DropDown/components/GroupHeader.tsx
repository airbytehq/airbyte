import React from "react";
import styled from "styled-components";

export type IProps = {
  item: string;
};

const GroupText = styled.div<{ empty?: boolean }>`
  color: ${({ theme }) => theme.textColor};
  border: none;
  padding: 10px 16px;
  font-size: 14px;
  line-height: 19px;
  border-top: 1px solid ${({ theme }) => theme.greyColor20};
  background: ${({ theme }) => theme.greyColor0};
  font-weight: normal;
  display: ${({ empty }) => (empty ? "none" : "block")};
`;

const GroupHeader: React.FC<IProps> = ({ item }) => (
  <GroupText empty={!item}>{item}</GroupText>
);

export default GroupHeader;

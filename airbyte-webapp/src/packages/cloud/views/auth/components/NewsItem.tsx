import React from "react";
import styled from "styled-components";

const Item = styled.div`
  box-shadow: 0 2px 4px 0 rgba(26, 25, 77, 0.12);
  border-radius: 12px;
  background: ${({ theme }) => theme.whiteColor};
  padding: 23px 23px 20px 15px;
  margin-bottom: 12px;
  font-weight: 500;
  font-size: 18px;
  line-height: 22px;
`;

const BottomBlock = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

const Date = styled.div`
  color: ${({ theme }) => theme.greyColor40};
  font-style: normal;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
`;

const NewsItem: React.FC = () => {
  return (
    <Item>
      TEXT
      <BottomBlock>
        <Date>01/01/2020</Date>
        <div>icon</div>
      </BottomBlock>
    </Item>
  );
};

export default NewsItem;

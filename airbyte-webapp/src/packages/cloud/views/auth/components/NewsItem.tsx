import React from "react";
import styled from "styled-components";
import dayjs from "dayjs";
import { Card } from "components";

const NewsCard = styled(Card)`
  padding: 23px 23px 20px 15px;
  font-weight: 500;
  font-size: 18px;
  line-height: 22px;
`;

const BottomBlock = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin-top: 7px;
`;

const Date = styled.div`
  color: ${({ theme }) => theme.greyColor40};
  font-style: normal;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  align-self: center;
`;

const NewsItem: React.FC<{
  className?: string;
  text: string;
  date: dayjs.Dayjs;
  icon: string;
}> = (props) => {
  return (
    <NewsCard className={props.className}>
      {props.text}
      <BottomBlock>
        <Date>{props.date.format("MM/DD/YYYY")}</Date>
        <div>
          <img src={props.icon} alt="Logo" />
        </div>
      </BottomBlock>
    </NewsCard>
  );
};

export default NewsItem;

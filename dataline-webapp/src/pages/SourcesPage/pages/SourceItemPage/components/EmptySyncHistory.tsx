import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

type IProps = {
  text?: React.ReactNode;
};

const Content = styled.div`
  padding: 74px 0 111px;
  text-align: center;
  font-size: 20px;
  line-height: 27px;
  color: ${({ theme }) => theme.textColor};
`;

const ImgBlock = styled.div`
  height: 80px;
  width: 80px;
  border-radius: 50%;
  background: ${({ theme }) => theme.greyColor20};
  margin: 0 auto 10px;
  text-align: center;
  padding: 20px 0;
`;

const EmptySyncHistory: React.FC<IProps> = ({ text }) => (
  <Content>
    <ImgBlock>
      <img src="/cactus.png" height={40} alt={"cactus"} />
    </ImgBlock>
    {text || <FormattedMessage id="sources.noSync" />}
  </Content>
);

export default EmptySyncHistory;

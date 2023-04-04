import React, { useState, useEffect, useRef } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { EmailIcon } from "./EmailIcon";

const Container = styled.div<{
  offsetTop?: number;
}>`
  height: calc(100vh - ${({ offsetTop }) => offsetTop}px);
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
`;

const Title = styled.div`
  font-size: 36px;
  line-height: 42px;
  display: flex;
  align-items: center;
  color: #27272a;
  padding: 60px 0 20px 0;
`;

const Text = styled.div`
  white-space: pre-line;
  text-align: center;
  font-size: 16px;
  color: #6b6b6f;
  line-height: 30px;
`;

const SubmitSuccess: React.FC = () => {
  const [offsetTop, setOffsetTop] = useState<number>(70);

  const divRef = useRef(null);
  useEffect(() => {
    const top: number = divRef.current ? divRef.current?.["offsetTop"] + 150 : 0;
    setOffsetTop(top);
  }, []);

  return (
    <Container ref={divRef} offsetTop={offsetTop}>
      <EmailIcon />
      <Title>
        <FormattedMessage id="settings.support.submit.success.title" />
      </Title>
      <Text>
        <FormattedMessage id="settings.support.submit.success.text" />
      </Text>
    </Container>
  );
};

export default SubmitSuccess;

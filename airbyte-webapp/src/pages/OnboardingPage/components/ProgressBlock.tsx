import React from "react";
import { FormattedMessage } from "react-intl";
import styled, { keyframes } from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

const run = keyframes`
  from {
    background-position: 0 0;
  }

  to {
    background-position: 98% 0;
  }
`;

const Bar = styled.div`
  width: 100%;
  height: 49px;
  background: ${({ theme }) => theme.darkBeigeColor} url("/rectangle.svg");
  color: ${({ theme }) => theme.redColor};
  border-radius: 15px;
  font-weight: 500;
  font-size: 13px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;

  animation: ${run} 15s linear infinite;
`;
const Lnk = styled.span`
  font-weight: 600;
  text-decoration: underline;
  color: ${({ theme }) => theme.redColor};
  padding: 0 5px;
`;
const Img = styled.img`
  margin-right: 9px;
`;

const ProgressBlock: React.FC = () => {
  return (
    <Bar>
      <Img src={"/process-arrow.svg"} width={20} />
      <FormattedMessage
        id="onboarding.synchronisationProgress"
        values={{
          sr: (...sr: React.ReactNode[]) => (
            <>
              <Lnk>{sr}</Lnk> <FontAwesomeIcon icon={faChevronRight} />
            </>
          ),
          ds: (...ds: React.ReactNode[]) => <Lnk>{ds}</Lnk>,
          sync: (...sync: React.ReactNode[]) => <Lnk>{sync}</Lnk>,
        }}
      />
    </Bar>
  );
};

export default ProgressBlock;

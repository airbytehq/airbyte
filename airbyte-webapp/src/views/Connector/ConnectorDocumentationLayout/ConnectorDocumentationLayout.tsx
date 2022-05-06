import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import styled from "styled-components";

const PanelGrabber = styled.div`
  height: 100vh;
  padding: 6px;
  display: flex;
`;

const GrabberHandle = styled(FontAwesomeIcon)`
  margin: auto;
  height: 25px;
  color: ${({ theme }) => theme.greyColor20};
`;

export const ConnectorDocumentationLayout = ({ children }: { children: [React.ReactNode, React.ReactNode] }) => {
  const [left, right] = children;
  return (
    <ReflexContainer orientation="vertical" windowResizeAware={true}>
      <ReflexElement className="left-pane"> {left}</ReflexElement>
      <ReflexSplitter style={{ border: 0, background: "rgba(255, 165, 0, 0)" }}>
        <PanelGrabber>
          <GrabberHandle icon={faGripLinesVertical} size={"1x"} />
        </PanelGrabber>
      </ReflexSplitter>
      <ReflexElement className="right-pane" size={1000}>
        {right}
      </ReflexElement>
    </ReflexContainer>
  );
};

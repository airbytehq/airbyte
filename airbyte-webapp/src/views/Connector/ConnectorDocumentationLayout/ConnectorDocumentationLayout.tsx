import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import styled from "styled-components";

import { useDocumentationPanelContext } from "./ConnectorDocumentationContext";

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

//NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately.

export const ConnectorDocumentationLayout = ({ children }: { children: [React.ReactNode, React.ReactNode] }) => {
  const [left, right] = children;

  const { documentationPanelOpen } = useDocumentationPanelContext();

  return (
    <ReflexContainer orientation="vertical" windowResizeAware={true}>
      <ReflexElement className="left-pane"> {left}</ReflexElement>
      {documentationPanelOpen && (
        <ReflexSplitter style={{ border: 0, background: "rgba(255, 165, 0, 0)" }}>
          <PanelGrabber>
            <GrabberHandle icon={faGripLinesVertical} size={"1x"} />
          </PanelGrabber>
        </ReflexSplitter>
      )}
      {documentationPanelOpen && (
        <ReflexElement className="right-pane" size={1000}>
          {right}
        </ReflexElement>
      )}
    </ReflexContainer>
  );
};

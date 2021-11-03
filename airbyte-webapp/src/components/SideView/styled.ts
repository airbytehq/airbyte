import styled, { keyframes } from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const animate = keyframes`
  from {
    opacity: 0;
		transform: translate3d(100%, 0, 0);
  }

  to {
    opacity: 1;
		transform: none;
  }
`;

export const Actions = styled.div`
  display: flex;
  align-items: center;
`;

export const Body = styled.div`
  display: flex;
  flex-direction: column;
`;

export const Close = styled(FontAwesomeIcon)`
  cursor: pointer;
  font-size: 18px;
`;

export const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
`;

export const Container = styled.div`
  display: flex;
  position: absolute;
  z-index: 9998;
  width: 100vw;
  height: 100vh;
  top: 0;
  right: 0;
  justify-content: flex-end;
  background-color: rgba(32, 32, 32, 0.09);
`;

export const Content = styled.div`
  background-color: #fff;
  height: 100vh;
  width: 60vw;
  top: 0;
  right: 0;
  box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04),
    0 3px 14px 0 rgba(11, 10, 26, 0.08), 0 5px 5px 0 rgba(11, 10, 26, 0.12);
  padding: 20px 50px;
  overflow: scroll;
  animation-name: ${animate};
  animation-duration: 0.1s;
  animation-fill-mode: both;
`;

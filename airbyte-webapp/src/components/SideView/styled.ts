import styled, { keyframes } from "styled-components";

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
  padding: 70px 35px 20px;
`;

export const Close = styled.div`
  cursor: pointer;
  font-size: 18px;
  background-color: rgba(255, 255, 255, 0.1);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }
`;

export const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background-color: ${({ theme }) => theme.mediumPrimaryColor};
  padding: 0 20px;
  color: ${({ theme }) => theme.whiteColor};
  position: fixed;
  top: 0;
  width: 60vw;
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
  background-color: rgba(32, 32, 32, 0.2);
`;

export const Content = styled.div`
  background-color: #fff;
  height: 100vh;
  width: 60vw;
  top: 0;
  right: 0;
  box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04),
    0 3px 14px 0 rgba(11, 10, 26, 0.08), 0 5px 5px 0 rgba(11, 10, 26, 0.12);
  overflow: scroll;
  animation-name: ${animate};
  animation-duration: 0.1s;
  animation-fill-mode: both;
  position: relative;
`;

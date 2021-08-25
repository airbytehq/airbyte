import React from "react";
import styled from "styled-components";

type VideoItemProps = {
  videoLink?: string;
  description?: React.ReactNode;
};

const VideoBlock = styled.div`
  position: relative;
  width: 317px;
  height: 185px;
  filter: drop-shadow(0px 14.4px 14.4px rgba(26, 25, 77, 0.2));

  &:before,
  &:after {
    content: "";
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    border-radius: 7.2px;
  }

  &:before {
    width: 317px;
    height: 189px;
    transform: rotate(2.98deg);
    background: ${({ theme }) => theme.primaryColor};
    z-index: 1;
  }

  &:after {
    width: 320px;
    height: 184px;
    transform: rotate(-2.48deg);
    background: ${({ theme }) => theme.successColor};
    z-index: 2;
  }
`;

const VideoFrame = styled.div`
  position: relative;
  width: 317px;
  height: 185px;
  background: ${({ theme }) => theme.whiteColor};
  border: 2.4px solid ${({ theme }) => theme.whiteColor};
  box-shadow: 0 2.4px 4.8px rgba(26, 25, 77, 0.12),
    0 16.2px 7.2px -10.2px rgba(26, 25, 77, 0.2);
  border-radius: 7.2px;
  z-index: 3;
`;

const Description = styled.div`
  text-align: center;
  color: ${({ theme }) => theme.primaryColor};
  font-size: 13px;
  line-height: 20px;
  margin-top: 14px;
`;

const VideoItem: React.FC<VideoItemProps> = ({ description }) => {
  return (
    <div>
      <VideoBlock>
        <VideoFrame />
      </VideoBlock>
      <Description>{description}</Description>
    </div>
  );
};

export default VideoItem;

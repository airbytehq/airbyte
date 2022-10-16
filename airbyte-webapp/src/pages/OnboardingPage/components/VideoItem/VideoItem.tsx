import React, { useState } from "react";
import styled from "styled-components";

import PlayButton from "./components/PlayButton";
import ShowVideo from "./components/ShowVideo";

interface VideoItemProps {
  small?: boolean;
  videoId?: string;
  link?: string;
  img?: string;
  description?: React.ReactNode;
}

const Content = styled.div<{ small?: boolean }>`
  width: ${({ small }) => (small ? 158 : 317)}px;
  text-decoration: none;
`;

const VideoBlock = styled.div<{ small?: boolean }>`
  position: relative;
  width: 100%;
  height: ${({ small }) => (small ? 92 : 185)}px;
  filter: drop-shadow(0px 14.4px 14.4px rgba(26, 25, 77, 0.2));

  &:before,
  &:after {
    content: "";
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    border-radius: ${({ small }) => (small ? 3.6 : 7.2)}px;
  }

  &:before {
    width: ${({ small }) => (small ? 158 : 317)}px;
    height: ${({ small }) => (small ? 94 : 189)}px;
    transform: rotate(2.98deg);
    background: ${({ theme }) => theme.primaryColor};
    z-index: 1;
  }

  &:after {
    width: ${({ small }) => (small ? 160 : 320)}px;
    height: ${({ small }) => (small ? 92 : 184)}px;
    transform: rotate(-2.48deg);
    background: ${({ theme }) => theme.successColor};
    z-index: 2;
  }
`;

const VideoFrame = styled.div<{ small?: boolean; img?: string }>`
  cursor: pointer;
  position: relative;
  width: ${({ small }) => (small ? 158 : 317)}px;
  height: ${({ small }) => (small ? 92 : 185)}px;
  background: ${({ theme }) => theme.whiteColor} ${({ img }) => (img ? `url(${img})` : "")};
  background-size: cover;
  border: 2.4px solid ${({ theme }) => theme.whiteColor};
  box-shadow: 0 2.4px 4.8px rgba(26, 25, 77, 0.12), 0 16.2px 7.2px -10.2px rgba(26, 25, 77, 0.2);
  border-radius: ${({ small }) => (small ? 3.6 : 7.2)}px;
  z-index: 3;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const Description = styled.div<{ small?: boolean }>`
  text-align: center;
  color: ${({ theme, small }) => (small ? theme.textColor : theme.primaryColor)};
  font-size: 13px;
  line-height: ${({ small }) => (small ? 16 : 20)}px;
  margin-top: 14px;
  cursor: pointer;
`;

const VideoItem: React.FC<VideoItemProps> = ({ description, small, videoId, img, link }) => {
  const [isVideoOpen, setIsVideoOpen] = useState(false);
  const onOpenVideo = () => videoId && setIsVideoOpen(true);
  const isLink = !!link && !videoId;

  const contentProps = isLink ? { href: link, target: "_blanc" } : {};

  return (
    <Content small={small} as={isLink ? "a" : "div"} {...contentProps}>
      <VideoBlock small={small}>
        <VideoFrame small={small} img={img} onClick={onOpenVideo}>
          <PlayButton small={small} onClick={onOpenVideo} isLink={isLink} />
        </VideoFrame>
      </VideoBlock>
      <Description small={small} onClick={onOpenVideo}>
        {description}
      </Description>
      {isVideoOpen ? <ShowVideo videoId={videoId} onClose={() => setIsVideoOpen(false)} /> : null}
    </Content>
  );
};

export default VideoItem;

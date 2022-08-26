import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

import { Button } from "components/base";
import Modal from "components/Modal";

interface ShowVideoProps {
  videoId?: string;
  onClose: () => void;
}

const CloseButton = styled(Button)`
  position: absolute;
  top: 30px;
  right: 30px;
  color: ${({ theme }) => theme.whiteColor};
  font-size: 20px;

  &:hover {
    border: none;
  }
`;

const ShowVideo: React.FC<ShowVideoProps> = ({ videoId, onClose }) => {
  return (
    <Modal onClose={onClose} clear closeOnBackground>
      <CloseButton onClick={onClose} iconOnly>
        <FontAwesomeIcon icon={faTimes} />
      </CloseButton>
      <iframe
        width="940"
        height="528"
        src={`https://www.youtube.com/embed/${videoId}`}
        title="YouTube video player"
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      />
    </Modal>
  );
};

export default ShowVideo;

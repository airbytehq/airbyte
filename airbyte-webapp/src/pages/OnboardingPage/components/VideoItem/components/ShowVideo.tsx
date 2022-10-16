import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";

import { Button } from "components/ui/Button";
import { Modal } from "components/ui/Modal";

import styles from "./ShowVideo.module.scss";

interface ShowVideoProps {
  videoId?: string;
  onClose: () => void;
}

const ShowVideo: React.FC<ShowVideoProps> = ({ videoId, onClose }) => {
  return (
    <Modal onClose={onClose} cardless>
      <Button className={styles.closeButton} onClick={onClose} icon={<FontAwesomeIcon icon={faTimes} />} />
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

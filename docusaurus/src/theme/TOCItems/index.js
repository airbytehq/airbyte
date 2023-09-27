import React, { useState } from 'react';
import TOCItems from '@theme-original/TOCItems';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faThumbsDown, faThumbsUp } from '@fortawesome/free-regular-svg-icons';

import styles from "./TOCItemsWrapper.module.css";

export default function TOCItemsWrapper(props) {
  const [voted, setVoted] = useState(false);
  const onVote = (vote) => {
    // Send to Segment (which should be injected in this page by Cloudflare)
    window.analytics?.track?.("rate_page", {
      page: window.location.pathname,
      page_title: document.title,
      vote,
    });
    setVoted(true);
  };
  return (
    <>
      <TOCItems {...props} />
      <div className={styles.pageRate}>
        <div>Was this page helpful?</div>
        {!voted ?
          <div className={styles.buttonWrapper}>
            <button className={styles.rateButton} onClick={() => onVote("up")}>
              <FontAwesomeIcon icon={faThumbsUp} size="lg" className={styles.rateButton} />
              Yes
            </button>
            <button className={styles.rateButton} onClick={() => onVote("down")}>
              <FontAwesomeIcon icon={faThumbsDown} size="lg" className={styles.rateButton} />
              No
            </button>
          </div>
          :
          <div className={styles.thanks}>Thank you!</div>
        }
      </div>
    </>
  );
}

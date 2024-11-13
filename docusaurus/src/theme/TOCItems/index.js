import { faThumbsDown, faThumbsUp } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import TOCItems from "@theme-original/TOCItems";
import React, { useState } from "react";
import { RequestERD } from "../../components/RequestERD/RequestERD";

import styles from "./TOCItemsWrapper.module.css";

function showDocSurvey() {
  const showSurvey = () => {
    chmln.show("6525a7ef3f4f150011627c9f");
  };

  if (!window.chmln) {
    // Initialize Chameleon if it's not loaded already
    !(function (d, w) {
      var t =
          "SaG54hxuMI4CDIZa2yBv4lX1NHVB0jQBNTORqyAN2p2tE4-1OtIxC-DS9ywbXXIr2TPyYr",
        c = "chmln",
        i = d.createElement("script");
      if ((w[c] || (w[c] = {}), !w[c].root)) {
        (w[c].accountToken = t),
          (w[c].location = w.location.href.toString()),
          (w[c].now = new Date()),
          (w[c].fastUrl = "https://fast.chameleon.io/");
        var m =
          "identify alias track clear set show on off custom help _data".split(
            " "
          );
        for (var s = 0; s < m.length; s++) {
          !(function () {
            var t = (w[c][m[s] + "_a"] = []);
            w[c][m[s]] = function () {
              t.push(arguments);
            };
          })();
        }
        (i.src = w[c].fastUrl + "messo/" + t + "/messo.min.js"),
          (i.async = !0),
          d.head.appendChild(i);
      }
    })(document, window);
    // As soon as it's loaded show the survey
    window.chmln.on("load:chmln", showSurvey);
    // Identify the user reusing the segment id if possible
    window.chmln.identify(
      window.analytics?.user().id() ??
        window.analytics?.user().anonymousId() ??
        "chmln-no-segment-user",
      {}
    );
  } else {
    showSurvey();
  }
}

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
    if (vote === "down") {
      showDocSurvey();
    }
  };
  return (
    <>
      <TOCItems {...props} />
      <RequestERD />
      <div className={styles.pageRate}>
        <div>Was this page helpful?</div>
        {!voted ? (
          <div className={styles.buttonWrapper}>
            <button className={styles.rateButton} onClick={() => onVote("up")}>
              <FontAwesomeIcon
                icon={faThumbsUp}
                size="lg"
                className={styles.rateButton}
              />
              Yes
            </button>
            <button
              className={styles.rateButton}
              onClick={() => onVote("down")}
            >
              <FontAwesomeIcon
                icon={faThumbsDown}
                size="lg"
                className={styles.rateButton}
              />
              No
            </button>
          </div>
        ) : (
          <div className={styles.thanks}>Thank you!</div>
        )}
      </div>
    </>
  );
}

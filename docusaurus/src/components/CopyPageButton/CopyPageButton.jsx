import Link from "@docusaurus/Link";

import { useLocation } from "@docusaurus/router";
import useIsBrowser from '@docusaurus/useIsBrowser';

import { faMarkdown } from "@fortawesome/free-brands-svg-icons";
import {
  faArrowUpRightFromSquare,
  faCheck,
  faChevronDown,
  faClone,
  faRobot,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from "@headlessui/react";
import React from "react";
import styles from "./CopyPageButton.module.css";


export const CopyPageButton = () => {
  const [isCopied, setIsCopied] = React.useState(false);
  const location = useLocation();
  const currentPath = location.pathname;

  const isBrowser = useIsBrowser();

  // Remove trailing slash if present
  const normalizedPath =
    currentPath.endsWith("/") && currentPath !== "/"
      ? currentPath.slice(0, -1)
      : currentPath;

  // Path to the markdown file - handle root path specially
  const mdPath = normalizedPath === "/" ? "index.md" : `${normalizedPath}.md`;

  const fullMdUrl =
  isBrowser
      ? `${window.location.origin}/${mdPath.replace(/^\//, "")}`
      : undefined;

  const handleCopyPage = async () => {
    const pageContent = await fetch(mdPath).then((res) => res.text());
    navigator.clipboard.writeText(pageContent);
    setIsCopied(true);
    setTimeout(() => {
      setIsCopied(false);
    }, 2500);
  };

  const chatGptUrl = `https://chat.openai.com/?q=Read+from+${fullMdUrl}+so+I+can+ask+questions+about+it`;

  return (
    <div className={styles.container}>
      <Button className={styles.copyButton} onClick={handleCopyPage}>
        {isCopied ? (
          <>
            <FontAwesomeIcon icon={faCheck} className={styles.menuItemIcon} />{" "}
            <span className={styles.menuItemTitle}>Copied</span>
          </>
        ) : (
          <>
            <FontAwesomeIcon icon={faClone} className={styles.menuItemIcon} />{" "}
            <span className={styles.menuItemTitle}> Copy Page</span>
          </>
        )}
      </Button>
      <Menu as="div">
        <MenuButton className={styles.dropdownButton}>
          <FontAwesomeIcon icon={faChevronDown} />
        </MenuButton>
        <MenuItems className={styles.menuItems}>
          <MenuItem>
            <Button className={styles.menuItem} onClick={handleCopyPage}>
              <FontAwesomeIcon icon={faClone} className={styles.menuItemIcon} />
              <div className={styles.menuItemContent}>
                <div className={styles.menuItemTitle}>Copy page</div>
                <div className={styles.menuItemDescription}>
                  Copy page as Markdown for LLMs
                </div>
              </div>
            </Button>
          </MenuItem>
          <MenuItem>
            <Link className={styles.menuItem} to={mdPath} target="_blank">
              <FontAwesomeIcon
                icon={faMarkdown}
                className={styles.menuItemIcon}
              />
              <div className={styles.menuItemContent}>
                <div className={styles.menuItemTitle}>View as Markdown</div>
                <div className={styles.menuItemDescription}>
                  View this page as plain text{" "}
                  <FontAwesomeIcon
                    icon={faArrowUpRightFromSquare}
                    className={styles.inlineIcon}
                  />
                </div>
              </div>
            </Link>
          </MenuItem>
          {isBrowser && fullMdUrl && (
            <MenuItem>
              <a
                className={styles.menuItem}
                href={chatGptUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <FontAwesomeIcon
                  icon={faRobot}
                  className={styles.menuItemIcon}
                />
                <div className={styles.menuItemContent}>
                  <div className={styles.menuItemTitle}>Open in ChatGPT</div>
                  <div className={styles.menuItemDescription}>
                    Ask questions about this page
                  </div>
                </div>
              </a>
            </MenuItem>
          )}
        </MenuItems>
      </Menu>
    </div>
  );
};

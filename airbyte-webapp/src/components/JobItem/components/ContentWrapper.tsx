import { motion } from "framer-motion";
import React from "react";

import styles from "./ContentWrapper.module.scss";

interface IProps {
  children?: React.ReactNode;
  isOpen?: boolean;
  onToggled?: () => void;
}

const ContentWrapper: React.FC<React.PropsWithChildren<IProps>> = ({ children, isOpen, onToggled }) => {
  return (
    <motion.div
      className={styles.container}
      animate={!isOpen ? "closed" : "open"}
      onAnimationComplete={onToggled}
      variants={{
        open: {
          height: "auto",
          opacity: 1,
          transition: { type: "tween" },
        },
        closed: {
          height: "0",
          opacity: 0,
          transition: { type: "tween" },
        },
      }}
    >
      {children}
    </motion.div>
  );
};

export default ContentWrapper;

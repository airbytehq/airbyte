import { motion } from "framer-motion";
import React from "react";

interface Props {
  children?: React.ReactNode;
  isOpen?: boolean;
  openedCallback?: () => void;
}

const ContentWrapper: React.FC<Props> = ({ children, isOpen, openedCallback }) => {
  return (
    <motion.div
      animate={!isOpen ? "closed" : "open"}
      variants={{
        open: {
          height: "auto",
          opacity: 1,
          transition: { type: "tween" },
        },
        closed: {
          height: "1px",
          opacity: 0,
          transition: { type: "tween" },
        },
      }}
      onAnimationComplete={() => openedCallback?.()}
    >
      {children}
    </motion.div>
  );
};

export default ContentWrapper;

import { motion } from "framer-motion";
import React from "react";

interface IProps {
  children?: React.ReactNode;
  isOpen?: boolean;
  onToggled?: () => void;
}

const ContentWrapper: React.FC<IProps> = ({ children, isOpen, onToggled }) => {
  return (
    <motion.div
      animate={!isOpen ? "closed" : "open"}
      onAnimationComplete={onToggled}
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
    >
      {children}
    </motion.div>
  );
};

export default ContentWrapper;

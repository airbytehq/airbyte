import { motion } from "framer-motion";
import React from "react";

interface IProps {
  children?: React.ReactNode;
  isOpen?: boolean;
}

const ContentWrapper: React.FC<IProps> = ({ children, isOpen }) => {
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
    >
      {children}
    </motion.div>
  );
};

export default ContentWrapper;

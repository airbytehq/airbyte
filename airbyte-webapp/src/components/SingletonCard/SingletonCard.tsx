import React from "react";

import MessageBox from "components/base/MessageBox";

interface SingletonCardProps {
  title: string | React.ReactNode;
  text?: string | React.ReactNode;
  hasError?: boolean;
  onClose?: () => void;
}

export const SingletonCard: React.FC<SingletonCardProps> = ({ title, text, onClose }) => {
  let message = "";
  if (title) {
    message += title;
  }
  if (title && text) {
    message += ": ";
  }
  if (text) {
    message += text;
  }

  return <MessageBox message={message} isString onClose={onClose} position="center" type="error" />;
};

export default SingletonCard;

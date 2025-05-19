import styles from "./ChatTrigger.module.css";

const ChatTrigger = () => {
  return (
    <button className={styles.chatTrigger}>
      <img src="/img/octavia-hello-no-text.png" alt="Octavia"  />
    </button>
  );
};

export default ChatTrigger;

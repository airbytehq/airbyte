import styles from "./ChatTrigger.module.css";
const Icon = () => {
  return (
    <span className={styles.chatTrigger__icon}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 16 16"
        data-icon="ai-stars"
        className={styles.chatTrigger__icon}
      >
        <path
          fill="url(#starsGradient)"
          d="m11.27 8.345-3.006-.458-1.346-2.72a.67.67 0 0 0-.602-.373.66.66 0 0 0-.573.372L4.397 7.887l-3.007.458c-.544.058-.744.745-.343 1.117l2.148 2.12-.516 3.007c-.057.4.286.744.659.744.114 0 .2 0 .315-.057l2.692-1.432 2.663 1.432c.115.057.2.057.315.057a.657.657 0 0 0 .659-.744l-.515-3.007 2.176-2.12c.372-.372.172-1.06-.372-1.117m-2.777 2.263-.516.487.115.716.286 1.575-1.403-.745-.63-.343-.659.343-1.403.745.286-1.575.115-.716-.516-.487L3.023 9.49l1.575-.23.716-.114 1.03-2.062.688 1.432.315.63.716.115 1.575.229zm1.976-5.356.745-1.517 1.546-.774-1.546-.744L10.469.67l-.773 1.547-1.518.744 1.518.774zm4.124.917-.458-.917-.459.917-.916.458.916.458.459.917.458-.917.916-.458z"
        ></path>
        <defs>
          <linearGradient
            id="starsGradient"
            x1="1.002"
            x2="13.002"
            y1="9.5"
            y2="10"
            gradientUnits="userSpaceOnUse"
          >
            <stop stop-color="hsl(241, 100%, 68%)"></stop>
            <stop offset="1" stop-color="hsl(10, 100%, 65%)"></stop>
          </linearGradient>
        </defs>
      </svg>
    </span>
  );
};
const ChatTrigger = () => {
  return (
    <button
      className={styles.chatTrigger}
      onClick={() => {
        window.analytics?.track("ask_ai_button_clicked");
      }}
    >
      <Icon />
      Ask AI
    </button>
  );
};

export default ChatTrigger;

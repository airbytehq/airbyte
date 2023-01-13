export const isCloudApp = () => (import.meta.env.REACT_APP_CLOUD || window.CLOUD) === "true";

export const isCloudApp = () => (process.env.REACT_APP_CLOUD || window.CLOUD) === "true";

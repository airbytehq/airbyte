import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";
function fetchAndUpdateCloudStatus(el) {
  // Load status from instatus and attach page status as CSS class
  // https://instatus.com/help/widgets/custom
  fetch("https://status.airbyte.com/summary.json")
    .then((resp) => resp.json())
    .then((summary) => {
      const status = summary.page.status;
      el?.classList.forEach((className) => {
        if (className.startsWith("status-")) {
          el.classList.remove(className);
        }
      });
      el?.classList.add(`status-${status.toLowerCase()}`);
    });
}

function pollForCloudStatusLinkAndUpdate() {
  let attempts = 0;
  const maxAttempts = 10;
  const interval = setInterval(() => {
    const el = document.querySelector(".cloudStatusLink");
    if (el) {
      clearInterval(interval);
      fetchAndUpdateCloudStatus(el);
    } else if (++attempts >= maxAttempts) {
      clearInterval(interval);
    }
  }, 800);
}
if (ExecutionEnvironment.canUseDOM) {
  setInterval(
    () => {
      // Check Cloud status every 10 minutes
      pollForCloudStatusLinkAndUpdate();
    },
    10 * 60 * 1000,
  );
  pollForCloudStatusLinkAndUpdate();
}

export const onRouteDidUpdate = ({ location, previousLocation }) => {
  if (
    !location.pathname.includes(previousLocation?.pathname) ||
    previousLocation?.pathname === "/"
  ) {
    pollForCloudStatusLinkAndUpdate();
  }
};

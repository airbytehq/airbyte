import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";

if (ExecutionEnvironment.canUseDOM) {
    function updateCloudStatus() {
      // Load status from instatus and attach page status as CSS class
      // https://instatus.com/help/widgets/custom
      fetch("https://status.airbyte.com/summary.json")
      .then((resp) => resp.json())
      .then((summary) => {
        const status = summary.page.status;
        const el = document.querySelector(".cloudStatusLink");
        el?.classList.forEach((className) => {
          if (className.startsWith("status-")) {
            el.classList.remove(className);
          }
        });
        el?.classList.add(`status-${status.toLowerCase()}`)
      });
  }

  setInterval(() => {
    // Check Cloud status every 10 minutes
    updateCloudStatus();
  }, 10 * 60 * 1000);

  setTimeout(() => {
    // Wait 1 execution slot for first status load, since the navigation bar might not have rendered yet
    updateCloudStatus();
  });
}
import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";

if (ExecutionEnvironment.canUseDOM) {
  // Pre-fetch the urls for the binaries.
  const binaries = fetch(
      'https://api.github.com/repos/airbytehq/abctl/releases/latest')
  .then(response => response.json())
  .then(data => data.assets);

  // Initialize button by choosing the relevant binary based on the data-architecture tag.
  function initializeDownloadButton(button) {
    binaries.then(assets => {
      const architecture = button.getAttribute('data-architecture');
      const binary = assets.find(
          b => b.name.toLowerCase().includes(architecture.toLowerCase()));
      if (binary) {
        button.href = binary.browser_download_url;
        button.innerText = `Download ${architecture}`;
      }
    })
    .catch(error => {
      console.error('Error fetching latest release:', error);
    });
  }

  // All buttons with this behavior have the class abctl-download.
  function initializeAllDownloadButtons() {
    const buttons = document.getElementsByClassName('abctl-download');
    Array.from(buttons).forEach(initializeDownloadButton);
  }

  // Document load is a bit weird in docusaurus.
  // https://stackoverflow.com/a/74736980/4195169
  window.addEventListener('load', () => {
    setTimeout(initializeAllDownloadButtons, 1000);
  });
}

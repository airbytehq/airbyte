import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";

if (ExecutionEnvironment.canUseDOM) {
  function initializeDownloadButton(button) {
    const architecture = button.getAttribute('data-architecture');
    fetch('https://api.github.com/repos/airbytehq/abctl/releases/latest')
    .then(response => response.json())
    .then(data => {
      const asset = data.assets.find(asset =>
          asset.name.toLowerCase().includes(architecture.toLowerCase())
      );
      if (asset) {
        button.href = asset.browser_download_url;
        button.innerText = `Download ${architecture}`;
        button.classList.remove('disabled');
      } else {
        fallback(button);
      }
    })
    .catch(error => {
      console.error('Error fetching latest release:', error);
      fallback(button);
    });
  }

  /*
   If loading fails for some reason or we can't find the asset, fallback on just
   making a link to the latest releases page.
  */
  function fallback(button) {
    button.href = 'https://github.com/airbytehq/abctl/releases/latest';
    button.innerText = `Latest ${architecture} Release`
    button.target = '_blank';  // Opens the link in a new tab
    button.classList.remove('disabled');
  }

  function initializeAllDownloadButtons() {
    const buttons = document.getElementsByClassName('abctl-download');
    Array.from(buttons).forEach(initializeDownloadButton);
  }

  function handleMutations(mutations) {
    for (let mutation of mutations) {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.classList.contains('abctl-download')) {
              initializeDownloadButton(node);
            } else {
              const buttons = node.getElementsByClassName('abctl-download');
              Array.from(buttons).forEach(initializeDownloadButton);
            }
          }
        });
      }
    }
  }

  window.addEventListener('load', initializeAllDownloadButtons);
  const observer = new MutationObserver(handleMutations);
  observer.observe(document.body, { childList: true, subtree: true });
}

document.addEventListener('DOMContentLoaded', function() {
  const button = document.getElementById('download-button');
  const repo = button.getAttribute('data-repo');

  button.innerText = 'Loading...';

  fetch(`https://api.github.com/repos/${repo}/releases/latest`)
  .then(response => response.json())
  .then(data => {
    const linuxAsset = data.assets.find(asset =>
        asset.name.toLowerCase().includes('amd64')
    );

    button.href = linuxAsset.browser_download_url;
    button.innerText = 'Download Latest Linux Release';
    button.classList.remove('disabled');
  })
  .catch(error => {
    console.error('Error fetching latest release:', error);
    button.innerText = 'Error Loading Release';
    button.classList.add('disabled');
  });
});

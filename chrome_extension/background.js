SERVER_URL = 'http://localhost:20456';


function startDownload(url, path) {
    xhr = new XMLHttpRequest();
    params = ['/?url=', encodeURIComponent(url),
              '&path=', encodeURIComponent(path)].join('');
    xhr.open('GET', SERVER_URL + params);
    xhr.send();
    // TODO: Fallback to Chrome if Flash is down.
}


chrome.downloads.onChanged.addListener(function(downloadDelta) {

    if (!downloadDelta.filename) {
        return;
    }

    chrome.downloads.search({'id': downloadDelta.id},
        function(downloadItems) {
            downloadItem = downloadItems[0];
            if (downloadItem.totalBytes < 1e7) {
                return;
            }
            startDownload(downloadItem.finalUrl,
                          downloadDelta.filename.current);
            chrome.downloads.cancel(downloadDelta.id);
        });
});

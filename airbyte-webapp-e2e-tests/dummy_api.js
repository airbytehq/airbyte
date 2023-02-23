// Script starting a basic webserver returning mocked data over an authenticated API to test the connector builder UI and connector builder server in an
// end to end fashion.

// Start with `npm run createdummyapi`

const http = require('http');

const items = [{ name: "abc" }, { name: "def" }, { name: "xxx" }, { name: "yyy" }];

const requestListener = function (req, res) {
  if (req.headers["authorization"] !== "Bearer theauthkey") {
    res.writeHead(403); res.end(JSON.stringify({ error: "Bad credentials" })); return;
  }
  if (req.url !== "/items") {
    res.writeHead(404); res.end(JSON.stringify({ error: "Not found" })); return;
  }
  // Add more dummy logic in here
  res.setHeader("Content-Type", "application/json");
  res.writeHead(200);
  res.end(JSON.stringify({ items: [...items].splice(req.headers["offset"] ? Number(req.headers["offset"]) : 0, 2) }));
}

const server = http.createServer(requestListener);
server.listen(6767);

process.on('SIGINT', function () {
  process.exit()
})

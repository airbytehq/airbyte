const http = require('http');

const requestListener = function (req, res) {
    if (req.url !== "/items") {
      res.writeHead(400); res.end(); return;
    }
    // Add more dummy logic in here
    res.setHeader("Content-Type", "application/json");
    res.writeHead(200);
    res.end(JSON.stringify({ items: [{ name: "abc"}, { name: "def" }]}));
}

const server = http.createServer(requestListener);
server.listen(6767);

process.on('SIGINT', function() {
    process.exit()
})

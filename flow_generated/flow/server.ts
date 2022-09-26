import * as http from 'http';

import { routes, Document, Lambda } from './routes';

// Server serves transform lambda invocation requests, streaming source
// collection documents, processing each via the designated transform, and
// streaming resulting derived documents in response.
export class Server {
    listenPath: string;

    constructor(listenPath: string) {
        this.listenPath = listenPath;
    }

    start(): void {
        const server = http.createServer(this._processStream.bind(this));
        server.on('error', console.error);
        server.listen({ path: this.listenPath });
    }

    _processStream(req: http.IncomingMessage, resp: http.ServerResponse): void {
        const malformed = (msg: string): void => {
            resp.setHeader('content-type', 'text/plain');
            resp.writeHead(400);
            resp.end(msg + '\n'); // Send message & EOF.
        };

        const path = req.url;
        if (path === undefined) {
            return malformed('expected url');
        }

        const lambda: Lambda | undefined = routes[path];
        if (lambda === undefined) {
            return malformed(`route ${path} is not defined`);
        }

        // Gather and join all data buffers.
        const chunks: string[] = [];

        req.on('data', (chunk: string) => {
            chunks.push(chunk);
        });

        req.on('end', () => {
            if (req.aborted) {
                return;
            }
            // Join input chunks and parse into an array of invocation rows.
            const [sources, registers] = JSON.parse(chunks.join('')) as [Document[], Document[][] | undefined];

            // Map each row into a future which will return Document[].
            const futures = sources.map(async (source, index) => {
                const previous = registers ? registers[index][0] : undefined;
                const register = registers ? registers[index][1] : undefined;

                return lambda(source, register || previous, previous);
            });

            // When all rows resolve, return the Document[][] to the caller.
            Promise.all(futures)
                .then((rows: Document[][]) => {
                    const body = Buffer.from(JSON.stringify(rows), 'utf8');
                    resp.setHeader('Content-Length', body.length);
                    resp.setHeader('Content-Type', 'application/json');
                    resp.writeHead(200);
                    resp.end(body);
                })
                .catch((err: Error) => {
                    // Send |err| to peer, and log to console.
                    resp.setHeader('content-type', 'text/plain');
                    resp.writeHead(400);
                    resp.end(`${err.name}: (${err.message})\n`);
                    console.error(err);
                });
        });

        req.on('error', (err) => {
            console.error(err);
        });
    }
}

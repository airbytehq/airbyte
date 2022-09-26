#!/usr/bin/env node
import { Server } from './server';

function main(): void {
    if (!process.env.SOCKET_PATH) {
        throw new Error('SOCKET_PATH environment variable is required');
    }
    new Server(process.env.SOCKET_PATH).start();

    console.error('READY');
}
main();

import process from 'node:process';
import readline from 'node:readline';
import {BufferListStream} from 'bl';

const ASCII_ETX_CODE = 0x03; // Ctrl+C emits this code

export class StdinDiscarder {
	#requests = 0;
	#mutedStream = new BufferListStream();
	#ourEmit;
	#rl;

	constructor() {
		this.#mutedStream.pipe(process.stdout);

		const self = this; // eslint-disable-line unicorn/no-this-assignment
		this.#ourEmit = function (event, data, ...args) {
			const {stdin} = process;
			if (self.#requests > 0 || stdin.emit === self.#ourEmit) {
				if (event === 'keypress') { // Fixes readline behavior
					return;
				}

				if (event === 'data' && data.includes(ASCII_ETX_CODE)) {
					process.emit('SIGINT');
				}

				Reflect.apply(self.#ourEmit, this, [event, data, ...args]);
			} else {
				Reflect.apply(process.stdin.emit, this, [event, data, ...args]);
			}
		};
	}

	start() {
		this.#requests++;

		if (this.#requests === 1) {
			this._realStart();
		}
	}

	stop() {
		if (this.#requests <= 0) {
			throw new Error('`stop` called more times than `start`');
		}

		this.#requests--;

		if (this.#requests === 0) {
			this._realStop();
		}
	}

	// TODO: Use private methods when targeting Node.js 14.
	_realStart() {
		// No known way to make it work reliably on Windows
		if (process.platform === 'win32') {
			return;
		}

		this.#rl = readline.createInterface({
			input: process.stdin,
			output: this.#mutedStream,
		});

		this.#rl.on('SIGINT', () => {
			if (process.listenerCount('SIGINT') === 0) {
				process.emit('SIGINT');
			} else {
				this.#rl.close();
				process.kill(process.pid, 'SIGINT');
			}
		});
	}

	_realStop() {
		if (process.platform === 'win32') {
			return;
		}

		this.#rl.close();
		this.#rl = undefined;
	}
}

import {ChildProcess} from 'child_process';
import spawn from 'cross-spawn';
import path from 'path';
import {Readable, Writable} from 'stream';

export async function read(s: Readable): Promise<string> {
  const lines: string[] = [];
  for await (const line of s) {
    lines.push(line);
  }
  return lines.join('\n');
}

export interface CLIOptions {
  env?: {[key: string]: string};
}

/** A convenience class for testing CLI inputs and outputs. */
export class CLI {
  constructor(private cp: ChildProcess) {}

  get stderr(): Readable {
    // `stderr` is always defined with the options in `runWith`.
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    return this.cp.stderr!;
  }

  get stdout(): Readable {
    // `stdout` is always defined with the options in `runWith`.
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    return this.cp.stdout!;
  }

  get stdin(): Writable {
    // `stdin` is always defined with the options in `runWith`.
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    return this.cp.stdin!;
  }

  /** Waits for the child process to terminate and returns the exit code. */
  async wait(): Promise<number> {
    return new Promise((ok) => {
      this.cp.on('exit', ok);
    });
  }

  /**
   * Checks stdin for the given prompt string, then writes the given response to
   * stdout.
   */
  respondToPrompt(prompt: string, response: string): void {
    // Use flag to only write to stdin once, since the Enquirer library prompt
    // triggers stdout.on() multiple times.
    let shouldRespond = true;
    this.stdout.on('data', (data: any) => {
      if (shouldRespond && data.toString().includes(prompt)) {
        this.stdin.write(response, 'utf8');
        shouldRespond = false;
      }
    });
  }

  /**
   * Runs CLI as a subprocess with the given arguments.
   *
   * If a home directory is not provided, the CLI's home directory will be set
   * to an empty, unique, and temporary directory. In particular, this means
   * that runs created by this function have separate caches and can run
   * concurrently without interference.
   *
   * If a home diectory is not provided, the newly generated temporary directory
   * will be deleted after the CLI command has returned. Otherwise, it is the
   * caller's responsibility to clean up their chosen home directory.
   */
  static async runWith(
    args: string[],
    opts: CLIOptions = {},
    bin = 'main'
  ): Promise<CLI> {
    const spawnOpts = {
      env: {
        ...process.env,
        ...opts.env,
      },
    };
    const cp = spawn(path.resolve('bin', bin), args, spawnOpts);
    return new CLI(cp);
  }
}

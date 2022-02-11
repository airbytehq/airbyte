#!/usr/bin/env python3

import os
import sys
import pty
import json
import time
import select
import signal
import logging
import tempfile

timeout = 14700
prefix = 'bg_wrapper.'
tmpdir = '/tmp'

pid = -1
status = 0
end_of_process = False


def signal_handler(signum, frame):

    global status
    global end_of_process

    (_, _status) = os.waitpid(pid, 0)
    status = os.WEXITSTATUS(_status)
    end_of_process = True


def redirect_stdout_stderr(fh):

    fp = open('/dev/null', 'r')
    os.dup2(fp.fileno(), sys.stdin.fileno())
    fp.close()

    os.dup2(fh, sys.stdout.fileno())
    os.dup2(fh, sys.stderr.fileno())

    os.close(fh)


def main(cmd):

    global pid
    global status
    global end_of_process

    (fh, logfile) = tempfile.mkstemp(prefix=prefix, dir=tmpdir)

    pid = os.fork()
    if pid:
        print(json.dumps({'pid':pid, 'logfile': logfile}))

    else:
        #os.chdir('/')
        os.setsid()
        redirect_stdout_stderr(fh)

        master, slave = pty.openpty()
        signal.signal(signal.SIGCHLD, signal_handler)
        poll = select.poll()
        poll.register(master, select.POLLIN|select.POLLPRI)

        pid = os.fork()
        if pid:
            os.close(slave)

            start_time = time.time()
            end_of_read = False

            logging.info('=== START ===\n')

            while not (end_of_process and end_of_read):

                if not end_of_read:

                    for fd, event in poll.poll(5*1000):

                        if event & select.POLLHUP:
                            poll.unregister(fd)
                            end_of_read = True

                        if event & (select.POLLIN|select.POLLPRI):
                            buff = os.read(master, 1024)
                            os.write(sys.stdout.fileno(), buff)

                if not end_of_process:

                    if time.time() - start_time > timeout:
                        os.kill(pid, signal.SIGKILL)
                        end_of_process = True

            print('', flush=True)
            logging.info('=== END (status: %d) ===', status)

        else:
            os.close(master)
            redirect_stdout_stderr(slave)
            os.execvp(cmd, sys.argv[1:])


if __name__ == '__main__':

    LOGGING_FORMAT = '%(asctime)-15s [bg_wrapper] %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)

    if len(sys.argv) < 2:
        print('%s prog [ args ]' % __file__, file=sys.stderr)
        sys.exit(1)

    cmd = os.path.realpath(sys.argv[1])
    main(cmd)

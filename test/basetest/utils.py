# -*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import socket
import signal
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from Queue import Queue, Empty
from time import sleep
from .exceptions import CommandError

USED_PORTS = set()
ON_POSIX = 'posix' in sys.builtin_module_names


def wait_process(proc, timeout=1):
    """Wait for process to finish
    """
    sleeptime = .1
    # Max number of attempts until giving up
    tries = int(timeout / sleeptime)

    # Wait for up to a second for the process to finish and avoid zombies
    for i in range(tries):
        exit = proc.poll()

        if exit is not None:
            break

        sleep(sleeptime)

    return exit


def _get_output(proc, input):
    """Collect output from the subprocess without blocking the main process if
    subprocess hangs.
    """
    def queue_output(proc, input, outq, errq):
        """Read/Write output/input of given process.
        This function is meant to be executed in a thread as it may block
        """
        # Send input and wait for finish
        out, err = proc.communicate(input)
        # Give the output back to the caller
        outq.put(out)
        errq.put(err)

    outq = Queue()
    errq = Queue()

    t = Thread(target=queue_output, args=(proc, input, outq, errq))
    t.daemon = True
    t.start()

    # A task process shouldn't take longer than 1 second to finish
    exit = wait_process(proc)

    # If it does take longer than 1 second, abort it
    if exit is None:
        proc.send_signal(signal.SIGABRT)
        exit = wait_process(proc)

    try:
        out = outq.get_nowait()
    except Empty:
        out = None
    try:
        err = errq.get_nowait()
    except Empty:
        err = None

    return out, err


def run_cmd_wait(cmd, input=None, stdout=PIPE, stderr=PIPE,
                 merge_streams=False, env=os.environ):
    "Run a subprocess and wait for it to finish"

    if input is None:
        stdin = None
    else:
        stdin = PIPE

    if merge_streams:
        stderr = STDOUT
    else:
        stderr = PIPE

    p = Popen(cmd, stdin=stdin, stdout=stdout, stderr=stderr, bufsize=1,
              close_fds=ON_POSIX, env=env)
    out, err = _get_output(p, input)

    if p.returncode != 0:
        raise CommandError(cmd, p.returncode, out, err)

    return p.returncode, out, err


def run_cmd_wait_nofail(*args, **kwargs):
    "Same as run_cmd_wait but silence the exception if it happens"
    try:
        return run_cmd_wait(*args, **kwargs)
    except CommandError as e:
        return e.code, e.out, e.err


def port_used(addr="localhost", port=None):
    "Return True if port is in use, False otherwise"
    if port is None:
        raise TypeError("Argument 'port' may not be None")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((addr, port))
    s.close()
    # result == 0 if connection was successful
    return result == 0


def find_unused_port(addr="localhost", start=53589, track=True):
    """Find an unused port starting at `start` port

    If track=False the returned port will not be marked as in-use and the code
    will rely entirely on the ability to connect to addr:port as detection
    mechanism. Note this may cause problems if ports are assigned but not used
    immediately
    """
    maxport = 65535
    unused = None

    for port in xrange(start, maxport):
        if not port_used(addr, port):
            if track and port in USED_PORTS:
                continue

            unused = port
            break

    if unused is None:
        raise ValueError("No available port in the range {0}-{1}".format(
            start, maxport))

    if track:
        USED_PORTS.add(unused)

    return unused


def release_port(port):
    """Forget that given port was marked as'in-use
    """
    try:
        USED_PORTS.remove(port)
    except KeyError:
        pass


try:
    from shutil import which
except ImportError:
    # NOTE: This is shutil.which backported from python-3.3.3
    def which(cmd, mode=os.F_OK | os.X_OK, path=None):
        """Given a command, mode, and a PATH string, return the path which
        conforms to the given mode on the PATH, or None if there is no such
        file.

        `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
        of os.environ.get("PATH"), or can be overridden with a custom search
        path.

        """
        # Check that a given file can be accessed with the correct mode.
        # Additionally check that `file` is not a directory, as on Windows
        # directories pass the os.access check.
        def _access_check(fn, mode):
            return (os.path.exists(fn) and os.access(fn, mode)
                    and not os.path.isdir(fn))

        # If we're given a path with a directory part, look it up directly
        # rather than referring to PATH directories. This includes checking
        # relative to the current directory, e.g. ./script
        if os.path.dirname(cmd):
            if _access_check(cmd, mode):
                return cmd
            return None

        if path is None:
            path = os.environ.get("PATH", os.defpath)
        if not path:
            return None
        path = path.split(os.pathsep)

        if sys.platform == "win32":
            # The current directory takes precedence on Windows.
            if os.curdir not in path:
                path.insert(0, os.curdir)

            # PATHEXT is necessary to check on Windows.
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            # See if the given file matches any of the expected path
            # extensions. This will allow us to short circuit when given
            # "python.exe". If it does match, only test that one, otherwise we
            # have to try others.
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext for ext in pathext]
        else:
            # On other platforms you don't have things like PATHEXT to tell you
            # what file suffixes are executable, so just pass on cmd as-is.
            files = [cmd]

        seen = set()
        for dir in path:
            normdir = os.path.normcase(dir)
            if normdir not in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.join(dir, thefile)
                    if _access_check(name, mode):
                        return name
        return None

# vim: ai sts=4 et sw=4

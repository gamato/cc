#######################
CC -- Command & Control
#######################
=============
CC components
=============

Daemons
#######

These are scripts that can be run alone or better launched & controlled by CC
Job Manager.


InfoScript (``infoscript``)
===========================

Runs a command / program periodically and sends its output.
Basically anything that can be run from shell and writes to standard
(and error) output can be handled.

Config options:
---------------

* ``info-script`` -- command line to execute

* ``info-period`` -- how often to execute command / program; in seconds

* ``info-name`` -- file name to use for command / program output (stdout + stderr)

* ``compression`` -- compression method to use for payload (output)

  - '', 'none', 'gzip', 'bzip2', 'xz'
  - defaults to no compression

* ``compression-level`` -- compression level to use (for gzip, bzip2, xz)

  - 1..9 where 1 is fastest and 9 is best ratio
  - default depends on compression method

* ``msg-suffix`` -- custom message type extension to use (for more flexible handling)

* ``use-blob`` -- whether to use blob for payload; boolean

  - default: yes

Config example:
---------------
::

    [d:infoscript]
    module = cc.daemon.infoscript
    info-name = info.server-stats.pl
    info-script = sudo -H -n -u nagios /home/nagios/server-stats.pl
    info-period = 10
    #compression = gzip
    #compression-level = 1


InfoSender (``infofile_collector``)
===================================

Collects and sends infofiles.  Basically it can monitor file system for any
files matching a mask (glob) and (re)sends them when they appear / change.

Config options:
---------------

* ``infodir`` -- directory to monitor

* ``infomask`` -- file mask (glob) to filter by

* ``compression`` -- compression method to use for payload (file contents)

  - '', 'none', 'gzip', 'bzip2', 'xz'
  - defaults to no compression

* ``compression-level`` -- compression level to use (for gzip, bzip2, xz)

  - 1..9 where 1 is fastest and 9 is best ratio
  - default depends on compression method

* ``msg-suffix`` -- custom message type extension to use (for more flexible handling)

* ``maint-period`` -- how often to do maintenance (cleaning up file cache); in seconds

  - default: 1 hour

* ``stats-period`` -- how often to send statistics out; in seconds

  - default: 30 seconds

* ``use-blob`` -- whether to use blob for payload; boolean

  - default: yes

Config example:
---------------
::

    [d:infosender]
    module = cc.daemon.infosender
    infodir = /home/nagios
    infomask = info.*
    #compression = gzip
    #compression-level = 1


LogfileTailer (``logfile_tailer``)
==================================

Logfile tailer for rotated log files.  It differs from InfoSender in that this
daemon tails files and sends data in chunks while InfoSender (re)sends whole
files.  It supports 2 operating modes: classic, rotated.

Assumes that:

- All log files reside in the same directory.
- We can find last log file by sorting the file list alphabetically.

In `classic` mode:

- When log is switched, the tailer continues tailing from the next file.
- When the tailer is restarted, it continues tailing from saved position.

In `rotated` mode:

- When log is switched, the tailer continues tailing from reopened file.

Config options:
---------------

* ``operation-mode`` -- mode of operation (see above)

  - 'classic', 'rotated'
  - default: classic

* ``logdir`` -- directory to monitor

* ``logmask`` -- file mask (glob) to filter by (for 'classic' mode)

* ``logname`` -- file name to watch & tail (for 'rotated' mode)

* ``lag-max-bytes`` -- maximum lag to try to catch up with; in bytes or other units

  - default: 0

* ``compression`` -- compression method to use for payload (file contents)

  - '', 'none', 'gzip', 'bzip2', 'xz'
  - defaults to no compression

* ``compression-level`` -- compression level to use (for gzip, bzip2, xz)

  - 1..9 where 1 is fastest and 9 is best ratio
  - default depends on compression method

* ``msg-suffix`` -- custom message type extension to use (for more flexible handling)

* ``buffer-bytes`` -- size of output (send) buffer to use; in bytes or other units

  - default: 1048576

* ``buffer-lines`` -- size of output (send) buffer to use; in lines

* ``use-blob`` -- whether to use blob for payload; boolean

  - default: yes

Config example:
---------------
::

    [d:logtail]
    module = cc.daemon.logtail
    logdir = /pg_log
    logmask = postgres*.log
    lag-max-bytes = 256 MB
    #compression = gzip
    #compression-level = 1


PgLogForward (``pg_logforward``)
================================

UDP server to handle UDP stream sent by pg_logforward_ (logging handler for PostgreSQL).

PgLogForward also serves as an example of how to extend daemons with plugins.
Plugins discovery, probing and loading is provided by CCDaemon class.
Plugins can be probed early (upon discovery) or late (upon loading).
This daemon and its plugins provide example implementation of both.

.. _pg_logforward: https://github.com/mpihlak/pg_logforward

Config options:
---------------

* ``listen-host`` -- host name or IP address on which to listen to incoming UDP stream

* ``listen-port`` -- port number on which to listen to incoming UDP stream

* ``log-format`` -- format of the incoming messages (datagrams)

  - 'json', 'netstr', 'syslog'

* ``plugins`` -- list of suitable plugins to use for processing of the incoming messages

* ``log-parsing-errors`` -- whether to log warning when parsing of received datagram fails; boolean

  - default: false

* ``stats-period`` -- how often to send statistics out; in seconds

  - default: 30 seconds

Config example:
---------------
::

    [d:pg_logforward]
    module = cc.daemon.pg_logforward
    listen-host = 0.0.0.0
    listen-port = 23456
    log-format = netstr
    plugins = p:logwatch

    [p:logwatch]
    module = cc.daemon.plugins.pg_logforward.example_logwatch


SkyLog (``skylog``)
===================

UDP server to handle UDP stream sent by SkyTools_' skylog.

.. _SkyTools: http://pgfoundry.org/projects/skytools

Config options:
---------------

* ``listen-host`` -- host name or IP address on which to listen to incoming UDP stream

* ``listen-port`` -- port number on which to listen to incoming UDP stream

* ``log-format`` -- format of the incoming messages (datagrams)

  - 'json', 'netstr', 'syslog'

* ``plugins`` -- list of suitable plugins to use for processing of the incoming messages

* ``log-parsing-errors`` -- whether to log warning when parsing of received datagram fails; boolean

  - default: false

* ``stats-period`` -- how often to send statistics out; in seconds

  - default: 30 seconds

Config example:
---------------
::

    [d:skylog]
    module = cc.daemon.skylog
    listen-host = 0.0.0.0
    listen-port = 12345
    log-format = netstr
    plugins =


TaskRunner (``task_runner``)
============================

Executes received tasks.  Watches running tasks.  Sends `task.register` message
periodically (for TaskRouter).

Config options:
---------------

* ``local-id`` -- TaskRunner name used to register with router(s)

* ``reg-period`` -- how often to register TaskRunner in central router; in seconds

  - default: 5 minutes

* ``maint-period`` -- how often to do maintenance (cleaning up task list); in seconds

  - default: 60 seconds

* ``task-grace-period`` -- how long for to remember task after it has finished; in seconds

  - default: 15 minutes

* ``task-heartbeat`` -- whether to send "task running" messages; boolean

  - default: false -- *Don't change!*

Config example:
---------------
::

    [d:taskrunner]
    module = cc.daemon.taskrunner
    local-id = myhostname
    #reg-period = 300
    #maint-period = 60

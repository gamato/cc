#######################
CC -- Command & Control
#######################
=============
CC components
=============

Handlers
########

CC handler classes are called in CC main loop, from single thread.
They need to do something with message received and fast.


DBHandler
=========

Sends request to database function and optionally returns its result (via reply message).

Config options:
---------------

* ``db`` -- database connection string

* ``allowed-functions`` -- function(s) allowed to be called

* ``worker-threads`` -- number of workers to start

  - default: 10

Config example:
---------------
::

    [h:testdb]
    handler = cc.handler.database
    db = dbname=test host=127.0.0.1 port=6001
    allowed-functions = public.func1, public.func2


Delay
=====

Delays all received messages, then dispatches them to another handler.

Config options:
---------------

* ``forward-to`` -- name of handler to forward messages to

* ``delay`` -- how long to delay received messages; in seconds

  - default: 0

Config example:
---------------
::

    [h:delay]
    handler = cc.handler.delay
    forward-to = h:proxy
    delay = 5


Disposer
========

Discards any message received.  Think of it as "/dev/null" for CC.

Config example:
---------------
::

    [h:disposer]
    handler = cc.handler.disposer


Echo
====

Echo service.  Think of it as "ping" for CC.

- Passive (implicit) echo responding.
- Active (explicit) echo requesting and monitoring.

Config options:
---------------

* ``ping-remotes`` -- URI(s) of remote CC instance(s) to ping

Config example:
---------------
::

    [h:echo]
    handler = cc.handler.echo
    #ping-remotes = tcp://127.0.0.1:10001


Filter
======

Filters received messages, then dispatches them to another handler.

Note that exclude list takes precedence over include list.
Message types can be specified using wildcards ('?', '*').

Config options:
---------------

* ``forward-to`` -- name of handler to forward messages to

* ``exclude`` -- list of message types to drop

  - default: empty

* ``include`` -- list of message types to keep

  - default: all

Config example:
---------------
::

    [h:filter]
    handler = cc.handler.filter
    forward-to = h:infowriter
    exclude = pub.infofile.harvester


InfoWriter
==========

Writes to files.  Can optionally (re)compress data and keep one backup per file.

Config options:
---------------

* ``dstdir`` -- directory where to store (write) received files

* ``dstmask`` -- file path / name format for received files; if defined it overrides `host-subdirs` option

  - 'hostname' -- host name
  - 'filepath' -- full path + file name
  - 'filename' -- file name (w/o any path)
  - example: ``%%(hostname)s/%%(filename)s`` is the same as ``host-subdirs=yes``

* ``host-subdirs`` -- whether to create sub-folders per host; boolean

  - default: no

* ``bakext`` -- if defined, what filename extension to use for backups

  - defaults to no backups

* ``write-compressed`` -- controls how file should be written, adding filename extension as appropriate

  - '', 'no' -- write file as it was on sender side
  - 'keep' -- write file as it was sent (possibly compressed)
  - 'yes' -- write file compressed (and possibly re-compress)
  - default: no

* ``compression`` -- compression method to use for payload (file contents)

  - 'gzip', 'bzip2', 'xz'

* ``compression-level`` -- compression level to use (for gzip, bzip2, xz)

  - 1..9 where 1 is fastest and 9 is best ratio
  - default depends on compression method

* ``worker-threads`` -- number of workers to start

  - default: 10

Config example:
---------------
::

    [h:infowriter]
    handler = cc.handler.infowriter
    dstdir = /tmp/infofiles
    host-subdirs = yes
    bakext = --prev
    #write-compressed = keep


JobMgr
======

Executes local daemons / tasks, provides them with config, watches and restarts
them if needed.

Config options:
---------------

* ``daemons`` -- daemons to manage; links to config sections for those daemons

* ``pidfiledir`` -- directory where to keep pid files of running processes

  - defaults to CC server pid folder

Config example:
---------------
::

    [h:jobmgr]
    handler = cc.handler.jobmgr
    daemons = d:infosender, d:infoscript, d:taskrunner


LocalLogger
===========

Logs as local log message.

Config example:
---------------
::

    [h:locallog]
    handler = cc.handler.locallogger


ProxyHandler
============

Simple proxy implementation.  Forwards messages between client(s) and remote CC
server(s).  Optionally, it can monitor its connection to remote CC instance by
sending echo requests.

Config options:
---------------

* ``remote-cc`` -- URI at which remote CC instance listens

* ``ping`` -- whether to keep pinging remote CC instance; boolean

  - default: no

* ``zmq_hwm`` -- ZMQ_HWM socket option (high water mark)

  - default: 100 -- *Careful changing!*

* ``zmq_linger`` -- ZMQ_LINGER socket option (linger period for socket shutdown)

  - default: 500 -- *Careful changing!*

* ``zmq_tcp_keepalive`` -- ZMQ_TCP_KEEPALIVE socket option (feature on/off switch)

  - default: on -- *Careful changing!*

* ``zmq_tcp_keepalive_intvl`` -- ZMQ_TCP_KEEPALIVE_INTVL socket option (keep-alive period in idle condition; in seconds)

  - default: 15 -- *Careful changing!*

* ``zmq_tcp_keepalive_idle`` -- ZMQ_TCP_KEEPALIVE_IDLE socket option (connection in idle before sending out keep-alive probes; in seconds)

  - default: 240 -- *Careful changing!*

* ``zmq_tcp_keepalive_cnt`` -- ZMQ_TCP_KEEPALIVE_CNT socket option (number of probes to send before declaring remote end not available)

  - default: 4 -- *Careful changing!*

Config example:
---------------
::

    [h:proxycc]
    handler = cc.handler.proxy
    remote-cc = tcp://127.0.0.1:10001


TailWriter
==========

Appends to files.  It differs from InfoWriter in that this handler appends data
(fragments) while InfoWriter (re)writes whole files.

Assumes that files with op_mode='rotated' attribute will not rotate more often
than once per second.

Config options:
---------------

* ``dstdir`` -- directory where to store (write) received files (data)

* ``dstmask`` -- file path / name format for received files; if defined it overrides `host-subdirs` option

  - 'hostname' -- host name
  - 'filepath' -- full path + file name
  - 'filename' -- file name (w/o any path)
  - example: ``%%(hostname)s/%%(filename)s`` is the same as ``host-subdirs=yes``

* ``host-subdirs`` -- whether to create sub-folders per host; boolean

  - default: no

* ``write-compressed`` -- controls how file should be written, adding filename extension as appropriate

  - '', 'no' -- write file as it was on sender side
  - 'keep' -- write file as it was sent (possibly compressed)
  - 'yes' -- write file compressed (and possibly re-compress)
  - default: no

* ``compression`` -- compression method to use for payload (file contents)

  - 'gzip', 'bzip2', 'xz'

* ``compression-level`` -- compression level to use (for gzip, bzip2, xz)

  - 1..9 where 1 is fastest and 9 is best ratio
  - default depends on compression method

* ``buffer-bytes`` -- size of compression buffer to use; in bytes or other units

  - default: 1048576

* ``maint-period`` -- how often to do maintenance (closing long-open files, flushing inactive files); in seconds

  - default: 3 seconds

* ``worker-threads`` -- number of workers to start

  - default: 10

Config example:
---------------
::

    [h:tailwriter]
    handler = cc.handler.tailwriter
    dstdir = /tmp/infofiles
    host-subdirs = yes
    #write-compressed = yes
    #compression = gzip
    #compression-level = 1


TaskRouter
==========

Routes task requests / replies between clients (requestors) and executors.
Keeps track of host and client (reply) routes. Expires old ones.

*One reason for using router is simplification of firewall rules.
Another reason is to avoid using listening components on host side.*

Config options:
---------------

* ``route-lifetime`` -- how long to keep route to host after last request for registration; in seconds

  - default: 60 minutes

* ``reply-timeout`` -- how long to keep mapping from task-uid to route-to-client after last msg seen; in seconds

  - default: 5 minutes

* ``maint-period`` -- how often to do maintenance (cleaning up route lists); in seconds

  - default: 60 seconds

Config example:
---------------
::

    [h:taskrouter]
    handler = cc.handler.taskrouter
    #route-lifetime = 3600
    #reply-timeout = 300
    #maint-period = 60

s3tpc messages
==============

This describes the design of the unix socket protocol, as provided by `s3tpd`
(transport daemon) and used by some `s3tpc` (tool).


Request requirements
--------------------

#### Requests from s3tpc

`s3tpc` can request a connection.
Further requests work with that connection.

For this connection a listen or connect request is done.

Both are acknowleged after `s3tpd` confirms the request.

Data can be enqueued to sent, and data reception requested.

The connection status can be queried, and some extra status requests can be
done, e.g. "currently connected with ground station".


#### Requests from s3tpd

`s3tpd` notifies the `s3tpc` tool about updates, so it can react to it.

Those updates can be of general state, or per connection information. Thus,
`s3tpd` pushes received data to `s3tpc` if it said it was ready for more.

It can send notification about connection state like `established`, `closed`,
`waiting`, `fail`.


State Handling
--------------

`s3tpc` has a worker thread which interacts with `s3tpd` over the unix socket.
Requests from the tool are acknowleged when `s3tpd` confirms the reception.

The tool can use the `libs3tpc` in blocking or non-blocking mode. When blocking,
the call is delayed (with wait/notify) until the worker thread gets the "go"
from `s3tpd` via the unix socket. In non-blocking mode, the tool has to query
the state itself, or provide a callback function.

Multiple requests can be enqueued, all of them will be processed, but there is
no guarantee of order. A tool must not submit a request if the dependent actions
have not been processed yet.


Messages
--------

Request messages:

* Connection creation request
* Connect or listen request
* Connection state query (for connection id)
* Send request
* Receive request
* Connection data amount request
* Leftover data retrieve

Response messages:

* Connection created
* Listen suceeded
* Connect enqueued
* Connection failed (refused, internal error, ...)
* Connection established
* Data to send was enqueued
* Data was received
* Data amount report
* Leftover data report


Format
------

```
8bit message type
32bit packet length from beginning
data, depending on message type
```

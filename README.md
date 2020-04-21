# netgammon
A backgammon game with graphic interface. There are local and network game modes.
For network game you should use _backgammon_server/bgp_server.py_ with parameters `host:port`.
In _config.py_ you should change variables `HOST` and `PORT` to host and port, which you
specified when starting _bgp_server.py_

Example of using:

    python bgp_server.py localhost:34299

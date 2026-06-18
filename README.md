# TCP-Server
A Python-based TCP socket server that authenticates a remote "robot" client and guides it back to the origin coordinates (0,0) on a Cartesian grid. This project models a strict, text-based network application protocol.

**Features**

    TCP Socket Communication: Listens on port 65432 for incoming client connections.

    Challenge-Response Auth: Validates clients using a multi-step handshake with pre-shared keys and custom integer hashing.

    Autonomous Pathfinding: Identifies client direction and dynamically transmits MOVE and TURN instructions based on grid location.

    Obstacle Detours: Detects coordinate stalls (collisions) and automatically triggers an obstacle-bypass routine.

**Protocol Format**

Messages are parsed byte-by-byte and strictly delimited by the ASCII sequence \a\b (\x07\x08).

**Navigation Loop**

    1) Server requests coordinates via 102 MOVE.

    2) Client responds with OK [X] [Y].

    3) Server calculates the optimal trajectory, commands turns if necessary, and repeats.

    4) Upon reaching (0,0), the server fetches the secret payload (105 GET MESSAGE) and logs out (106 LOGOUT).

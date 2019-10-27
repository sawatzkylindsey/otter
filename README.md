Otter
-----
Readable HTTP server library for lightweight applications.

Usage
-----

    # Run a server:
    # -hosted at localhost:8080
    # -Api endpoints rooted at /api
    # -resources served from the relative path /resources
    # -a single Api handler Echo located at /api/echo

    otter.server.run_server(8080, "api", "resources", {
        "echo": otter.handler.Echo(),
    })


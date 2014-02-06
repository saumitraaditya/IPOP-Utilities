IPOP Stats
==========

**Warning:** *This is under heavy development, and is not ready for use.*

*Gathers anonymous usage statistics of IPOP users.*

We need these statistics to justify our funding in grant proposals. They're
opt-in only, and the only information we collect is:

-   Your IP address
-   A randomly generated UUID
-   Client version number
-   The number of connections your node makes
-   If STUN or TURN is being used
-   The name of the controller (groupvpn or socialvpn)
-   Statistics about average connection lifetime

We'll never publish full database dumps, but we will publish general statistical
information from our database.

Testing
-------

```python
sudo aptitude install python3-pip
sudo pip3 install virtualenv
virtualenv -p python3 .env
.env/bin/pip install -e .
.env/bin/ipop-stats
```

Abuse
-----

It's possible for someone to write a client that abuses the API, spamming it
with artificially inflated statistics. We record IPs so we could perform some
analysis later to filter out these results, but heavily NATed environments could
complicate this.

Generally, we assume nobody will spam us with API calls, as there's no
motivation for an attacker to do so.

Upon setting up a production system, we should use some sort of rate-limiting,
to avoid being DoSed. [Nginx has a rate limiting module][nginx limit req].

*Please don't be evil!*

[nginx limit req]: http://nginx.org/en/docs/http/ngx_http_limit_req_module.html

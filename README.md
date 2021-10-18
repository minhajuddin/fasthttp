# FastHTTP

## Mission
Be the fastest, most robust, traceable and safe way to send HTTP requests to
External APIs

## Inspiration
  - Envoy edge proxy
  - Hystrix
  - Polly (.net)
  - Finagle

## Flow

(Your app)---SECURE CONNECTION-->(Fast HTTP)---HTTP requests--->(External API)

## Features
1. Retryable
2. Idempotency
3. Traceability
4. Circuit Breakers
5. Rate limiting
6. Respect caching and configure caching
7. Compressed reqs / responses
8. Backpressure
9. Configurable pool / connect / read timeouts
10. Persistent HTTP connections
11. Connection pooling
12. TLS verification
13. Rate limit (configurable)
14. Batch requests
15. Async requests
16. Fully traceable
17. Cluster for being fault tolerant
18. Did we say fast?
19. Respects idempotency keys and uses idempotency keys
20. Simple API

---
TODO from an older project

### MVP
- [ x ] AB should be able to create long living h2/http 1 connections to APIs
    -   We currently do this via Finch's connection pool

### V1
- [  ] Retryability [configurable]
- [  ] Idempotency IDs on non GET requests [configurable]
- [  ] Traceability
- [  ] Allow async requests: Send a request and forget about it!
- [  ] Circuit Breakers [configurable]
- [  ] Rate limiting [configurable]
- [  ] Respect Caching [configurable]
- [  ] Compressed reqs/responses? [configurable]
- [  ] Backpressure
- [  ] POOL timeouts currently go on forever, we should stop retrying after a large number
- [  ] Timeout for requests

### V2

- [  ] Support binary data in body via base64
- [  ] Support duplicate header values
- [  ] Connection pooling [configurable]
    -   We currently do this via Finch's connection pool
- [  ] Inspect status of various endpoints [by path]
  - [  ] Aggregate
    - [  ] Circuit breaker statuses
    - [  ] Rate limiter statuses
    - [  ] Reqs/second
    - [  ] Latencies
    - [  ] Throughput
    - [  ] Response status codes
    - [  ] Response status codes
  - [  ] Single request full request / response info
- [  ] Repeat a request (being able to replay a request and look at its results)

### V3

- [  ] Alerting (via DD)
- [  ] A client should be able to create long living h2 connections to AB


---

To start your Phoenix server:

  * Install dependencies with `mix deps.get`
  * Create and migrate your database with `mix ecto.setup`
  * Start Phoenix endpoint with `mix phx.server` or inside IEx with `iex -S mix phx.server`

Now you can visit [`localhost:4000`](http://localhost:4000) from your browser.

Ready to run in production? Please [check our deployment guides](https://hexdocs.pm/phoenix/deployment.html).

## Learn more

  * Official website: https://www.phoenixframework.org/
  * Guides: https://hexdocs.pm/phoenix/overview.html
  * Docs: https://hexdocs.pm/phoenix
  * Forum: https://elixirforum.com/c/phoenix-forum
  * Source: https://github.com/phoenixframework/phoenix

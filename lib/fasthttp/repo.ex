defmodule FastHTTP.Repo do
  use Ecto.Repo,
    otp_app: :fasthttp,
    adapter: Ecto.Adapters.Postgres
end

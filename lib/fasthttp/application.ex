defmodule FastHTTP.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Start the Ecto repository
      FastHTTP.Repo,
      # Start the Telemetry supervisor
      FastHTTPWeb.Telemetry,
      # Start the PubSub system
      {Phoenix.PubSub, name: FastHTTP.PubSub},
      {Task.Supervisor, name: FastHTTP.RequestTaskSupervisor},
      # Start the Endpoint (http/https)
      {Finch,
       name: FastHTTP.Pool,
       pools: %{
         default: [count: 10, size: 10]
       }},
      FastHTTPWeb.Endpoint
      # Start a worker by calling: FastHTTP.Worker.start_link(arg)
      # {FastHTTP.Worker, arg}
    ]

    :ok = FastHTTP.Telemetry.StatsdReporter.connect()

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: FastHTTP.Supervisor]
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    FastHTTPWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end

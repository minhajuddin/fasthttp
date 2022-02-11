# TODO: find a better name
# TODO: wire up telemetry to datadog
defmodule FastHTTP.Executor do
  require Logger

  def execute(requests) do
    Logger.info(log_code: "requests.create", requests: requests)

    # TODO: move this to a module
    requests
    |> Enum.map(fn request ->
      Task.Supervisor.async(FastHTTP.RequestTaskSupervisor, fn -> process_with_meta(request) end)
    end)
    |> Enum.map(fn task ->
      Task.await(task)
    end)
  end

  # TODO: meta should be shoved into headers
  defp process_with_meta(request) do
    {time_us, resp} = :timer.tc(fn -> process(request) end)

    meta = %{
      time_us: time_us
    }

    Map.put(resp, :meta, meta)
  end

  defp process(request) do
    req =
      Finch.build(
        parse_method(request["method"]),
        request["url"],
        parse_headers(request["headers"]),
        parse_body(request["body"])
      )

    # TODO: retries
    case Finch.request(req, FastHTTP.Pool) do
      {:ok, resp} ->
        IO.inspect(resp, label: "resp--------------------")

        %{
          id: request["id"],
          # TODO: think of a better name for this
          type: "response",
          status_code: resp.status,
          headers: Enum.map(resp.headers, &:erlang.tuple_to_list/1),
          body: resp.body
        }

      {:error, %Mint.TransportError{} = error} ->
        %{
          id: request["id"],
          type: "error",
          error_code: "transport_error",
          error_message: Exception.message(error)
        }
    end
  end

  defp parse_body(%{"type" => "empty"}), do: []
  defp parse_body(%{"type" => "string", "data" => body}), do: body
  # TODO: Handle this base64 errors
  defp parse_body(%{"type" => "base64", "data" => base64_body}), do: Base.decode64!(base64_body)

  # headers is a dict
  defp parse_headers(headers) do
    headers
    |> Enum.to_list()
  end

  for method <- [:get, :post, :put, :patch, :delete, :head, :options, :trace, :connect] do
    @method method
    @method_string method |> to_string |> String.upcase()

    defp parse_method(@method_string), do: @method
  end
end

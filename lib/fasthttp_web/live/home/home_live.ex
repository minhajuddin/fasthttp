defmodule FastHTTPWeb.Home.IndexLive do
  use FastHTTPWeb, :live_view

  @default_requests_json Jason.encode!([
                           %{
                             body: %{"type" => "empty"},
                             headers: %{
                               "accept" => "application/json",
                               "banana" => "apple",
                               "content-type" => "application/json"
                             },
                             id: Ecto.UUID.generate(),
                             method: "GET",
                             url: "https://httpbin.org/uuid"
                           },
                           %{
                             body: %{"type" => "empty"},
                             headers: %{
                               "accept" => "application/json",
                               "content-type" => "application/json"
                             },
                             id: Ecto.UUID.generate(),
                             method: "GET",
                             url: "https://httpbin.org/delay/0.5"
                           },
                           %{
                             body: %{"type" => "empty"},
                             headers: %{
                               "accept" => "application/json",
                               "content-type" => "application/json"
                             },
                             id: Ecto.UUID.generate(),
                             method: "GET",
                             url: "https://httpbin.org/delay/0.2"
                           },
                           %{
                             body: %{"type" => "empty"},
                             headers: %{
                               "accept" => "image/svg+xml"
                             },
                             id: Ecto.UUID.generate(),
                             method: "GET",
                             url: "https://httpbin.org/image"
                           }
                         ])

  @impl true
  def mount(_params, _session, socket) do
    {:ok, assign(socket, responses: [], requests_json: @default_requests_json, meta: %{})}
  end

  @impl true
  def handle_event("execute", %{"requests" => requests_json}, socket) do
    {real_time_us, {meta, responses}} = :timer.tc(fn -> execute(requests_json) end)

    {:noreply,
     assign(socket,
       responses: responses,
       requests_json: requests_json,
       meta: Map.put(meta, :real_time_ms, real_time_us / 1000)
     )}
  end

  defp execute(requests_json) do
    case Jason.decode(requests_json) do
      {:ok, requests} ->
        responses = FastHTTP.Executor.execute(requests)

        {%{
           request_count: length(responses),
           total_time_ms: (responses |> Enum.map(& &1.meta.time_us) |> Enum.sum()) / 1000
         }, responses}

      {:error, err} ->
        {0, "ERROR: #{inspect(err)}"}
    end
  end
end

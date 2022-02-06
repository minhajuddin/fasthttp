defmodule FastHTTPWeb.RequestController do
  use FastHTTPWeb, :controller
  require Logger


  def create(conn, %{"requests" => requests} = _params) do
    Logger.info(log_code: "requests.create", requests: requests)

    # TODO: move this to a module
    responses = requests
    |> Enum.map(&process/1)

    send_resp(conn, :ok, Jason.encode!(%{
      responses: responses
    }))
  end

  defp process(request) do
    req = Finch.build(
      parse_method(request["method"]),
      request["url"],
      parse_headers(request["headers"]),
      parse_body(request["body"]))

    # TODO handle errors
    {:ok, resp} = Finch.request(req, FastHTTP.Pool)
    IO.inspect(resp, label: "resp--------------------")
    %{
      id: request["id"],
      status_code: resp.status,
      headers: Enum.map(resp.headers, &:erlang.tuple_to_list/1),
      body: resp.body
    }
  end

  defp parse_body(%{"type" => "empty"}), do: []
  defp parse_body(%{"type" => "string", "data" => body}), do: body
  # TODO: Handle this base64 errors
  defp parse_body(%{"type" => "base64", "data" => base64_body}), do: Base.decode64!(base64_body)

  # headers is a dict
  defp parse_headers(headers) do
    headers
    |> Enum.to_list
  end


  for method <- [:get, :post, :put, :patch, :delete, :head, :options, :trace, :connect] do
    @method method
    @method_string (method |> to_string |> String.upcase)

    defp parse_method(@method_string), do: @method
  end
end

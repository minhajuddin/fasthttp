defmodule FastHTTPWeb.RequestController do
  use FastHTTPWeb, :controller

  def create(conn, %{"requests" => requests} = _params) do
    responses = FastHTTP.Executor.execute(requests)

    send_resp(
      conn,
      :ok,
      Jason.encode!(%{
        responses: responses
      })
    )
  end
end

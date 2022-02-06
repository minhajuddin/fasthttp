defmodule FastHTTPWeb.PageController do
  use FastHTTPWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end
end

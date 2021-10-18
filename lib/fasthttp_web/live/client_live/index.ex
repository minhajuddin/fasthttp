defmodule FastHTTPWeb.ClientLive.Index do
  use FastHTTPWeb, :live_view

  alias FastHTTP.Core
  alias FastHTTP.Core.Client

  @impl true
  def mount(_params, _session, socket) do
    {:ok, assign(socket, :clients, list_clients())}
  end

  @impl true
  def handle_params(params, _url, socket) do
    {:noreply, apply_action(socket, socket.assigns.live_action, params)}
  end

  defp apply_action(socket, :edit, %{"id" => id}) do
    socket
    |> assign(:page_title, "Edit Client")
    |> assign(:client, Core.get_client!(id))
  end

  defp apply_action(socket, :new, _params) do
    socket
    |> assign(:page_title, "New Client")
    |> assign(:client, %Client{})
  end

  defp apply_action(socket, :index, _params) do
    socket
    |> assign(:page_title, "Listing Clients")
    |> assign(:client, nil)
  end

  @impl true
  def handle_event("delete", %{"id" => id}, socket) do
    client = Core.get_client!(id)
    {:ok, _} = Core.delete_client(client)

    {:noreply, assign(socket, :clients, list_clients())}
  end

  defp list_clients do
    Core.list_clients()
  end
end

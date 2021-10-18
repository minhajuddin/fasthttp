defmodule FastHTTP.CoreTest do
  use FastHTTP.DataCase

  alias FastHTTP.Core

  describe "clients" do
    alias FastHTTP.Core.Client

    import FastHTTP.CoreFixtures

    @invalid_attrs %{name: nil, notes: nil}

    test "list_clients/0 returns all clients" do
      client = client_fixture()
      assert Core.list_clients() == [client]
    end

    test "get_client!/1 returns the client with given id" do
      client = client_fixture()
      assert Core.get_client!(client.id) == client
    end

    test "create_client/1 with valid data creates a client" do
      valid_attrs = %{name: "some name", notes: "some notes"}

      assert {:ok, %Client{} = client} = Core.create_client(valid_attrs)
      assert client.name == "some name"
      assert client.notes == "some notes"
    end

    test "create_client/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Core.create_client(@invalid_attrs)
    end

    test "update_client/2 with valid data updates the client" do
      client = client_fixture()
      update_attrs = %{name: "some updated name", notes: "some updated notes"}

      assert {:ok, %Client{} = client} = Core.update_client(client, update_attrs)
      assert client.name == "some updated name"
      assert client.notes == "some updated notes"
    end

    test "update_client/2 with invalid data returns error changeset" do
      client = client_fixture()
      assert {:error, %Ecto.Changeset{}} = Core.update_client(client, @invalid_attrs)
      assert client == Core.get_client!(client.id)
    end

    test "delete_client/1 deletes the client" do
      client = client_fixture()
      assert {:ok, %Client{}} = Core.delete_client(client)
      assert_raise Ecto.NoResultsError, fn -> Core.get_client!(client.id) end
    end

    test "change_client/1 returns a client changeset" do
      client = client_fixture()
      assert %Ecto.Changeset{} = Core.change_client(client)
    end
  end
end

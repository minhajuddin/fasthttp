defmodule FastHTTP.Core.Client do
  use Ecto.Schema
  import Ecto.Changeset

  @doc """
  A client controls the behavior of all requests that are sent through it.

  Here are a few things you can configure in a client:

  1. Timeouts
    - Pool timeout
    - Connect timeout
    - Read timeout
  2. Retry policy
  3. Cache policy
  4. Stale data policy aka fallback aka degrade gracefully
  5. Connection pooling policy
  6. Socket options like keepalives etc,.
  7. Circuit Breaker
  8. Request Queuing policy
  9. Bulkhead policy
  """

  @primary_key {:id, :binary_id, autogenerate: true}
  @foreign_key_type :binary_id
  schema "clients" do
    field :name, :string
    field :notes, :string

    timestamps()
  end

  @doc false
  def changeset(client, attrs) do
    client
    |> cast(attrs, [:name, :notes])
    |> validate_required([:name, :notes])
  end
end

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import json

import time

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
query trades{
  swaps(where:{pair: "0xdfa42ba0130425b21a1568507b084cc246fb0c8f"}, orderBy: timestamp, orderDirection: asc, first:3, block: {number:12328864 }) {
    id
    timestamp
    amount0In
    amount1In
    amount0Out
    amount1Out
    pair {
      token0 {
        id
        symbol
      }
      token1 {
        id
        symbol
      }
    }
    transaction {
      blockNumber
    }
  }
}
"""
)

# Execute the query on the transport
result = client.execute(query)


# parsed = json.loads(result)
print(json.dumps(result, indent=4, sort_keys=True))

# print(result)

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

USER_RESERVES_QUERY = """
{{
  userReserves(where: {{ user: "{address}"}}) {{
    id
    reserve{{
      id
      symbol
    }}
    user {{
      id
    }}
  }}
}}"""
url = 'https://api.thegraph.com/subgraphs/name/aave/protocol-raw'
transport = RequestsHTTPTransport(url=url, retries=5)

try:
    client = Client(transport=transport, fetch_schema_from_transport=True)
except (requests.exceptions.RequestException) as e:
    raise ValueError(f'Failed to connect to the graph at {url} due to {str(e)}') from e

address = '0x2b888954421b424c5d3d9ce9bb67c9bd47537d12'
query = client.execute(
    gql(USER_RESERVES_QUERY.format(address=address.lower())),
)

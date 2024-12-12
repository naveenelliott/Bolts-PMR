import json
from time import time

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class InvalidQueryError(RuntimeError):
    """
    Exception raised when a GraphQL query is invalid.
    """

    pass


class GraphQLClient:
    """
    Machine client for the PlayerData GraphQL API.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://app.playerdata.co.uk",
    ):
        """
        Initialize an OAuth2 session for the PlayerData GraphQL API.

        Args:
            client_id (str): OAuth2 client ID.
            client_secret (str): OAuth2 client secret.
            base_url (str, optional): Service base URL. Defaults to "https://app.playerdata.co.uk".
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.token = None
        client = BackendApplicationClient(client_id=client_id)
        self.session = OAuth2Session(client=client)

    def _authorize_session(self):
        """
        Authorize the OAuth2 session by fetching a new token.
        """
        self.token = self.session.fetch_token(
            token_url=f"{self.base_url}/oauth/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    def _validate_token(self) -> bool:
        """
        Check if the current token is valid.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        if not self.token:
            return False

        if "expires_at" not in self.token.keys():
            return False

        if self.token["expires_at"] < time():
            return False

        return True
    
    def query(self, query: str, variables: dict, query_timeout: float = 30.0) -> dict:
        """
        Execute a GraphQL query against the PlayerData API.

        Args:
            query (str): GraphQL query string.
            variables (dict): Variables to pass to the query.
            query_timeout (float, optional): Timeout for the query execution in seconds. Defaults to 30.0.

        Returns:
            dict: Query response JSON.

        Raises:
            InvalidQueryError: If the GraphQL query is invalid or returns errors.
        """
        if not self._validate_token():
            self._authorize_session()

        response = self.session.request(
            "POST",
            url=f"{self.base_url}/api/graphql",
            data={"query": str(query), "variables": json.dumps(variables)},
            timeout=(3.0, query_timeout),
        )

        response.raise_for_status()
        response_json = response.json()
        errors = response_json.get("errors", [])
        if len(errors) > 0:
            raise InvalidQueryError(
                f"Invalid GraphQL query. Received the following errors: {errors}"
            )

        return response_json

    def __del__(self):
        """
        Close the session when the object is deleted.
        """
        self.session.close()

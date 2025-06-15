import requests
from typing import Optional, Dict, Any
from mindsdb.integrations.libs.api_handler import APIHandler
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
    RESPONSE_TYPE
)
from mindsdb.utilities import log
from mindsdb_sql_parser import parse_sql
from .whale_alerts_tables import (
    TransactionsTable,
    StatusTable,
    BlockchainsTable
)

logger = log.getLogger(__name__)


class WhaleAlertsHandler(APIHandler):
    """
    The Whale Alerts handler implementation.
    """
    
    name = 'whale_alerts'
    
    def __init__(self, name: str, **kwargs):
        """
        Initialize the Whale Alerts handler.
        
        Args:
            name (str): The handler name
            kwargs: Connection arguments including api_key
        """
        super().__init__(name)
        
        # Connection parameters
        connection_data = kwargs.get('connection_data', {})
        self.api_key = connection_data.get('api_key')
        self.base_url = connection_data.get('base_url', 'https://api.whale-alert.io/v1')
        
        # API configuration
        self.headers = {
            'User-Agent': 'MindsDB-WhaleAlerts-Handler/1.0',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            self.headers['X-WA-API-KEY'] = self.api_key
        
        # Register available tables
        self._register_table('transactions', TransactionsTable(self))
        self._register_table('status', StatusTable(self))
        self._register_table('blockchains', BlockchainsTable(self))
        
    def connect(self) -> StatusResponse:
        """
        Set up any connections required by the handler.
        
        Returns:
            HandlerStatusResponse
        """
        try:
            # Test connection by checking API status
            response = self.call_whale_alerts_api('/status')
            if response and response.get('result') == 'success':
                self.is_connected = True
                return StatusResponse(True)
            else:
                self.is_connected = False
                return StatusResponse(False, "Connection failed: Invalid response from Whale Alerts API")
        except Exception as e:
            self.is_connected = False
            logger.error(f"Error connecting to Whale Alerts: {e}")
            return StatusResponse(False, f"Connection failed: {str(e)}")
    
    def check_connection(self) -> StatusResponse:
        """
        Check if the connection is alive and healthy.
        
        Returns:
            HandlerStatusResponse
        """
        return self.connect()
    
    def native_query(self, query: str) -> Response:
        """
        Receive and process a raw query.
        
        Args:
            query (str): query in native format
            
        Returns:
            HandlerResponse
        """
        ast = parse_sql(query, dialect='mindsdb')
        return self.query(ast)
    
    def call_whale_alerts_api(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Call Whale Alerts API endpoint.
        
        Args:
            endpoint (str): API endpoint path
            params (dict): Optional query parameters
            
        Returns:
            API response data
        """
        url = self.base_url + endpoint
        
        # Add API key to params if using query parameter method
        if self.api_key and 'X-WA-API-KEY' not in self.headers:
            if params is None:
                params = {}
            params['api_key'] = self.api_key
        
        try:
            response = requests.get(url, headers=self.headers, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API call: {e}")
            raise 
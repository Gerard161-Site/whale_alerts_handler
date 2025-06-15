from typing import List, Optional, Dict, Any
from mindsdb.integrations.libs.api_handler import APITable
from mindsdb.integrations.utilities.sql_utils import extract_comparison_conditions
from mindsdb_sql_parser.ast import Constant
import pandas as pd
import time


class TransactionsTable(APITable):
    """Table for whale transaction alerts."""
    
    def get_columns(self) -> List[str]:
        return [
            'blockchain', 'symbol', 'transaction_type', 'hash', 'from_address',
            'from_owner', 'from_owner_type', 'to_address', 'to_owner', 'to_owner_type',
            'timestamp', 'amount', 'amount_usd', 'transaction_count'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get whale transaction alerts."""
        conditions = extract_comparison_conditions(query.where)
        
        # Parse conditions
        blockchain = None
        currency = None
        min_value = 500000  # Default minimum value
        start_time = None
        end_time = None
        
        for op, arg1, arg2 in conditions:
            if arg1 == 'blockchain' and op == '=':
                blockchain = arg2
            elif arg1 == 'currency' and op == '=':
                currency = arg2
            elif arg1 == 'min_value' and op == '=':
                min_value = arg2
            elif arg1 == 'start_time' and op == '=':
                start_time = arg2
            elif arg1 == 'end_time' and op == '=':
                end_time = arg2
        
        # Set up parameters
        params = {
            'min_value': min_value
        }
        
        # Add start time (required parameter)
        if start_time:
            params['start'] = int(start_time)
        else:
            # Default to last 24 hours
            params['start'] = int(time.time() - 86400)
        
        if end_time:
            params['end'] = int(end_time)
        
        if currency:
            params['currency'] = currency
        
        # Get data from API
        response = self.handler.call_whale_alerts_api('/transactions', params)
        
        if response and response.get('result') == 'success' and 'transactions' in response:
            rows = []
            for tx in response['transactions']:
                # Filter by blockchain if specified
                if blockchain and tx.get('blockchain', '').lower() != blockchain.lower():
                    continue
                
                from_info = tx.get('from', {})
                to_info = tx.get('to', {})
                
                rows.append([
                    tx.get('blockchain'),
                    tx.get('symbol'),
                    tx.get('transaction_type'),
                    tx.get('hash'),
                    from_info.get('address'),
                    from_info.get('owner'),
                    from_info.get('owner_type'),
                    to_info.get('address'),
                    to_info.get('owner'),
                    to_info.get('owner_type'),
                    tx.get('timestamp'),
                    tx.get('amount'),
                    tx.get('amount_usd'),
                    tx.get('transaction_count')
                ])
            return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())


class StatusTable(APITable):
    """Table for Whale Alert service status."""
    
    def get_columns(self) -> List[str]:
        return [
            'result', 'blockchain_count', 'blockchain_name', 'symbols', 'status'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get Whale Alert service status."""
        response = self.handler.call_whale_alerts_api('/status')
        
        if response and response.get('result') == 'success':
            rows = []
            for blockchain in response.get('blockchains', []):
                rows.append([
                    response.get('result'),
                    response.get('blockchain_count'),
                    blockchain.get('name'),
                    ','.join(blockchain.get('symbols', [])),
                    blockchain.get('status')
                ])
            return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())


class BlockchainsTable(APITable):
    """Table for supported blockchains information."""
    
    def get_columns(self) -> List[str]:
        return [
            'name', 'symbols', 'status', 'symbol_count'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get supported blockchains information."""
        response = self.handler.call_whale_alerts_api('/status')
        
        if response and response.get('result') == 'success':
            rows = []
            for blockchain in response.get('blockchains', []):
                symbols = blockchain.get('symbols', [])
                rows.append([
                    blockchain.get('name'),
                    ','.join(symbols),
                    blockchain.get('status'),
                    len(symbols)
                ])
            return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns()) 
# Whale Alerts Handler

The Whale Alerts handler for MindsDB provides seamless integration with the Whale Alert API, enabling you to access large cryptocurrency transaction alerts and blockchain whale movements directly from your MindsDB instance.

## Implementation

This handler is implemented using the Whale Alert API and provides access to whale transaction data through SQL queries.

## Whale Alert API

Whale Alert is a platform that tracks large cryptocurrency transactions across multiple blockchains. It provides real-time alerts for significant movements of cryptocurrencies, helping traders and analysts monitor whale activity that might impact market prices.

## Connection

### Parameters

* `api_key`: Your Whale Alert API key (required)
* `base_url`: Whale Alert API base URL (default: `https://api.whale-alert.io/v1`)

### Example Connection

```sql
CREATE DATABASE whale_alerts_datasource
WITH ENGINE = "whale_alerts",
PARAMETERS = {
    "api_key": "your_whale_alert_api_key_here",
    "base_url": "https://api.whale-alert.io/v1"
};
```

## Getting an API Key

1. Visit [Whale Alert](https://whale-alert.io/)
2. Sign up for an account
3. Navigate to your dashboard
4. Generate an API key
5. Choose your subscription plan (free tier available)

## Usage

The available tables are:

* `transactions` - Large cryptocurrency transactions
* `status` - API status and statistics
* `blockchains` - Supported blockchains information

### Transactions Table

Get whale transaction alerts:

```sql
-- Get recent whale transactions
SELECT * FROM whale_alerts_datasource.transactions 
ORDER BY timestamp DESC 
LIMIT 20;

-- Get transactions for specific blockchain
SELECT * FROM whale_alerts_datasource.transactions 
WHERE blockchain = 'bitcoin'
ORDER BY amount_usd DESC;

-- Get transactions for specific symbol
SELECT * FROM whale_alerts_datasource.transactions 
WHERE symbol = 'BTC'
ORDER BY timestamp DESC;

-- Get transactions above certain USD value
SELECT * FROM whale_alerts_datasource.transactions 
WHERE amount_usd > 10000000  -- $10M+
ORDER BY amount_usd DESC;
```

### Status Table

Get API status and usage statistics:

```sql
-- Get current API status
SELECT * FROM whale_alerts_datasource.status;
```

### Blockchains Table  

Get information about supported blockchains:

```sql
-- Get all supported blockchains
SELECT * FROM whale_alerts_datasource.blockchains;

-- Get specific blockchain info
SELECT * FROM whale_alerts_datasource.blockchains 
WHERE name = 'ethereum';
```

## Data Types and Columns

### Transactions Table
- `blockchain` - Blockchain where transaction occurred
- `symbol` - Cryptocurrency symbol (BTC, ETH, etc.)
- `transaction_type` - Type of transaction (transfer, mint, burn)
- `hash` - Transaction hash
- `from_address` - Sender address
- `from_owner` - Sender owner (if known)
- `from_owner_type` - Sender type (exchange, whale, etc.)
- `to_address` - Recipient address
- `to_owner` - Recipient owner (if known)
- `to_owner_type` - Recipient type (exchange, whale, etc.)
- `timestamp` - Transaction timestamp
- `amount` - Transaction amount in cryptocurrency
- `amount_usd` - Transaction amount in USD
- `transaction_count` - Number of transactions in batch

### Status Table
- `status` - API status
- `usage` - Current usage statistics
- `limits` - API rate limits
- `remaining` - Remaining API calls
- `reset_time` - When limits reset

### Blockchains Table
- `name` - Blockchain name
- `symbol` - Native token symbol
- `network_id` - Network identifier
- `is_active` - Whether blockchain monitoring is active
- `min_amount_usd` - Minimum transaction amount to trigger alert

## Use Cases

### 1. Market Analysis
Monitor large transactions that might indicate:
- Whale accumulation or distribution
- Exchange inflows/outflows
- Institutional movements

```sql
-- Find large exchange outflows (potential selling pressure)
SELECT blockchain, symbol, amount_usd, from_owner, to_owner
FROM whale_alerts_datasource.transactions 
WHERE from_owner_type = 'exchange' 
AND to_owner_type = 'unknown'
AND amount_usd > 5000000
ORDER BY timestamp DESC;
```

### 2. Trend Monitoring
Track patterns in whale behavior:

```sql
-- Monitor Bitcoin whale movements
SELECT 
    DATE(FROM_UNIXTIME(timestamp)) as date,
    COUNT(*) as transaction_count,
    SUM(amount_usd) as total_usd_moved,
    AVG(amount_usd) as avg_transaction_size
FROM whale_alerts_datasource.transactions 
WHERE symbol = 'BTC'
GROUP BY DATE(FROM_UNIXTIME(timestamp))
ORDER BY date DESC;
```

### 3. Exchange Monitoring
Track large exchange movements:

```sql
-- Monitor exchange-to-exchange transfers
SELECT blockchain, symbol, amount_usd, from_owner, to_owner, timestamp
FROM whale_alerts_datasource.transactions 
WHERE from_owner_type = 'exchange' 
AND to_owner_type = 'exchange'
AND amount_usd > 1000000
ORDER BY timestamp DESC;
```

### 4. Alert Systems
Create custom alerts for significant movements:

```sql
-- Create alerts for massive transactions (>$50M)
SELECT 
    blockchain,
    symbol,
    amount_usd,
    from_owner,
    to_owner,
    'MEGA_WHALE_ALERT' as alert_type
FROM whale_alerts_datasource.transactions 
WHERE amount_usd > 50000000
ORDER BY timestamp DESC;
```

## Filtering Options

### By Blockchain
- `bitcoin` - Bitcoin network
- `ethereum` - Ethereum network
- `binance-smart-chain` - BSC
- `polygon` - Polygon network
- `avalanche` - Avalanche network
- And many more...

### By Transaction Type
- `transfer` - Regular transfers
- `mint` - Token minting
- `burn` - Token burning

### By Owner Type
- `exchange` - Cryptocurrency exchanges
- `whale` - Known whale addresses
- `unknown` - Unidentified addresses
- `defi` - DeFi protocols
- `institution` - Institutional addresses

## Limitations

- API requires a valid API key
- Rate limits apply based on subscription tier
- Free tier has limited requests per day
- Historical data availability depends on subscription
- Some very recent transactions might have delays

## Rate Limits

Rate limits vary by subscription tier:
- **Free**: 100 requests per day
- **Starter**: 1,000 requests per day
- **Professional**: 10,000 requests per day
- **Enterprise**: Custom limits

## Error Handling

The handler includes comprehensive error handling for:
- Invalid API keys
- Rate limiting
- Network connectivity issues
- Invalid parameters
- Missing data

## Best Practices

1. **Filter Wisely**: Use WHERE clauses to reduce API calls
2. **Cache Results**: Store frequently accessed data locally
3. **Monitor Limits**: Check your API usage regularly
4. **Batch Queries**: Combine multiple conditions in single queries
5. **Use Timestamps**: Query recent data to stay within limits

## Notes

- All timestamps are Unix timestamps
- USD values are calculated at transaction time
- Some addresses may not have owner information
- Transaction amounts are in the native cryptocurrency units
- The API updates continuously with new whale movements 
from langchain.tools import tool
from dotenv import load_dotenv
from utils.logger import get_logger
import os
import requests
import json

# Setup Logger
_logs = get_logger(__name__)
# Load environment variables and secrets
load_dotenv()
load_dotenv(".secrets")



@tool
def get_end_of_day_data(
        symbols="CX", price_currency='USD', exchange="XNYS", 
        date_from="2025-11-01", date_to="2025-11-10"):
    """
    Get information about stock ticker symbols.

    """
    _logs.debug(f'Retrieving market data for ticker/s {symbols} and exchange {exchange} between {date_from} and {date_to}')
    api_key = os.getenv("MARKETSTACK_ACCESS_KEY")

    url = "http://api.marketstack.com/v2/eod"

    params = {
        "access_key": api_key,
        "symbols": symbols,
        "price_currency": price_currency,
        "exchange": exchange,
        "sort": "DESC",
        "date_from": date_from,
        "date_to": date_to,
        "limit ": 200,
        "offset": 0,

    }

    response = requests.get(url, params=params)

    # Check if request was successful
    if response.status_code == 200:        
        resp_dict = json.loads(response.text)
        prices = resp_dict.get("data", [])
        return prices
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        _logs.warning(f'API did not return market prices. Error: {response.status_code}')
        return f"Error: {response.status_code}"
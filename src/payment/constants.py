from enum import Enum

class ErrorCode:
    AUTHENTICATION_REQUIRED = "Authentication required."
    AUTHORIZATION_FAILED = "Authorization failed. User has no access."
    INVALID_TOKEN = "Invalid token."
    INVALID_CREDENTIALS = "Invalid credentials."
    REFRESH_TOKEN_NOT_VALID = "Refresh token is not valid."
    REFRESH_TOKEN_REQUIRED = "Refresh token is required either in the body or cookie."
    INIT_DATA_NOT_VALID = "Init data is not valid."


class Network(Enum):
    ETH = "Ethereum"
    MATIC = "Polygon"
    ARBITRUM = "Arbitrum"
    
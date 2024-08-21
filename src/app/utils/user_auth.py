import hashlib
import hmac
from datetime import UTC, datetime, timedelta

from app.schemas import UserLogin


def user_auth(user_login: UserLogin, bot_token: str) -> UserLogin | None:
    check_hash = user_login.hash
    del user_login.hash

    data_check_arr = []
    for key, value in user_login.items():
        data_check_arr.append(f"{key}={value}")

    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_value = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if hash_value == check_hash and (
        datetime.now(UTC) - user_login.auth_date
    ) < timedelta(days=1):
        return user_login
    return None

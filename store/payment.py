import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings


# ==================================================================
# JAZZCASH — Page Redirection API (v1.1)
# ==================================================================

def build_jazzcash_payload(order):
    """
    Order ke liye JazzCash ko bhejne wala secure form-data taiyar karta hai.
    Amount PAISA mein hota hai (Rs. 500 = 50000).
    """
    now = datetime.now()
    txn_datetime = now.strftime("%Y%m%d%H%M%S")
    txn_expiry = (now + timedelta(minutes=30)).strftime("%Y%m%d%H%M%S")

    data = {
        "pp_Version": "1.1",
        "pp_TxnType": "MWALLET",
        "pp_Language": "EN",
        "pp_MerchantID": settings.JAZZCASH_MERCHANT_ID,
        "pp_Password": settings.JAZZCASH_PASSWORD,
        "pp_TxnRefNo": order.order_number,
        "pp_Amount": str(int(order.total * 100)),
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": txn_datetime,
        "pp_BillReference": order.order_number,
        "pp_Description": f"Order {order.order_number}",
        "pp_TxnExpiryDateTime": txn_expiry,
        "pp_ReturnURL": settings.JAZZCASH_RETURN_URL,
        "ppmpf_1": "",
        "ppmpf_2": "",
        "ppmpf_3": "",
        "ppmpf_4": "",
        "ppmpf_5": "",
    }

    data["pp_SecureHash"] = _jazzcash_hash(data)
    return data


def _jazzcash_hash(data):
    """
    HMAC-SHA256 hash. Sorted keys ki VALUES ko '&' se jodo,
    Integrity Salt ko shuru mein lagao, phir Integrity Salt hi
    secret key ki tarah use karke HMAC banao.
    """
    salt = settings.JAZZCASH_INTEGRITY_SALT
    sorted_keys = sorted(data.keys())
    values = "&".join(str(data[k]) for k in sorted_keys if data[k] != "")
    message = f"{salt}&{values}"

    digest = hmac.new(
        salt.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return digest


def verify_jazzcash_response(post_data):
    """
    JazzCash callback se aayi request ka hash dobara calculate karke
    match karta hai. False aaye to request FAKE hai — reject karo.
    """
    received_hash = post_data.get("pp_SecureHash", "")
    data_to_check = {k: v for k, v in post_data.items() if k != "pp_SecureHash"}

    recalculated = _jazzcash_hash(data_to_check)

    is_valid = hmac.compare_digest(received_hash, recalculated)
    is_success = post_data.get("pp_ResponseCode") == "000"

    return is_valid and is_success


# ==================================================================
# EASYPAISA — Hosted Checkout
# ==================================================================
# NOTE: EasyPaisa ka exact hash/encryption formula har merchant
# account type ke sath thora farq hota hai (kabhi HMAC, kabhi AES
# encryption). Neeche wala HMAC-SHA256 wala tareeqa sabse common
# hai, lekin GO-LIVE se pehle apni EasyPaisa merchant onboarding
# team se mile hue PDF/integration guide se is function ko
# zaroor cross-check kar lein.

def build_easypaisa_payload(order):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    expiry = (datetime.now() + timedelta(minutes=30)).strftime("%Y%m%d%H%M%S")

    data = {
        "storeId": settings.EASYPAISA_STORE_ID,
        "amount": f"{order.total:.1f}",
        "postBackURL": settings.EASYPAISA_RETURN_URL,
        "orderRefNum": order.order_number,
        "paymentMethod": "InitialRequest",
        "timeStamp": timestamp,
        "expiryDate": expiry,
        "autoRedirect": "1",
        "emailAddr": order.email or "",
        "mobileNum": order.phone,
    }

    data["merchantHashedReq"] = _easypaisa_hash(data)
    return data


def _easypaisa_hash(data):
    salt = settings.EASYPAISA_HASH_KEY
    sorted_keys = sorted(data.keys())
    values = "&".join(str(data[k]) for k in sorted_keys if data[k] != "")
    message = f"{salt}&{values}"

    digest = hmac.new(
        salt.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return digest


def verify_easypaisa_response(post_data):
    received_hash = post_data.get("merchantHashedReq", "")
    data_to_check = {k: v for k, v in post_data.items() if k != "merchantHashedReq"}

    recalculated = _easypaisa_hash(data_to_check)

    is_valid = hmac.compare_digest(received_hash, recalculated)
    is_success = post_data.get("responseCode") == "0000"

    return is_valid and is_success
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from aiohttp import ClientSession

import firebase_admin
from firebase_admin import credentials

import jwt


def load_private_key(path):
    with open(path, 'rb') as file:
        data = file.read()
        key = serialization.load_pem_private_key(data, None, default_backend())
        if not isinstance(key, RSAPrivateKey):
            raise TypeError(
                f"File [{path}] should be RSA PRIVATE KEY")

        return key


def generate_github_gwt_token(*, path, application_id):
    key = load_private_key(path)
    time_since_epoch = int(time.time())
    payload = {
        'iat': time_since_epoch,
        'exp': time_since_epoch + 600,
        'iss': application_id
    }
    token = jwt.encode(payload, key, algorithm='RS256')
    return token.decode()


def get_aiohttp_client_for_github(*, jwt_token, loop):
    headers = {
        'Accept': 'application/vnd.github.machine-man-preview+json',
        'Authorization': f'Bearer {jwt_token}'
    }
    return ClientSession(loop=loop)

def extract_bearer_token(token: str):
    return token.strip().partition(" ")[2]


def get_firebase_client(path):
    cred = credentials.Certificate(path)
    return firebase_admin.initialize_app(cred)

# def get_default_bot(user_id: str):
#     return {
#         "_id": user_id,
#         "name": "New bot",
#         "repositories": [],
#         "settings": {
#             "staleissue": {
#                 "enabled": False,
#                 "stale_days": 60,
#                 "close_days": 7,
#                 "stale_labels": ["wontfix"],
#                 "except_labels": ["security"],
#                 "stale_comment": "This issue was marked as stale due to inactivity",
#                 "close_comment": "This stale issue was closed due to inactivity"
#             },
#             "stalepullrequest": {
#                 "enabled": False,
#                 "stale_days": 60,
#                 "close_days": 7,
#                 "stale_labels": ["wontfix"],
#                 "except_labels": ["security"],
#                 "stale_comment": "This pull request was marked as stale due to inactivity",
#                 "close_comment": "This stale pull request was closed due to inactivity"
#             }
#         }
#     }

def get_default_bot():
    return {
        "name": "New bot",
        "repositories": [],
        "settings": {
            "staleissue": {
                "enabled": False,
                "stale_days": 60,
                "close_days": 7,
                "stale_labels": ["wontfix"],
                "except_labels": ["security"],
                "stale_comment": "This issue was marked as stale due to inactivity",
                "close_comment": "This stale issue was closed due to inactivity"
            },
            "stalepullrequest": {
                "enabled": False,
                "stale_days": 60,
                "close_days": 7,
                "stale_labels": ["wontfix"],
                "except_labels": ["security"],
                "stale_comment": "This pull request was marked as stale due to inactivity",
                "close_comment": "This stale pull request was closed due to inactivity"
            }
        }
    }
    

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

user_data_path = '/home/ubuntu/VoicingAI-pingone/data/users.json'
ENVIRONMENT_ID = "124e4bee-0fe0-440a-9ec0-960b1461585c"  
PINGONE_AUTH_TOKEN = os.getenv('PINGONE_AUTH_TOKEN')  

def list_users(access_token, environment_id, limit=3):
    """
    Fetch the list of users from PingOne.

    :param access_token: The access token for authentication.
    :param environment_id: The PingOne environment ID.
    :param limit: The number of users to retrieve (default is 3).
    :return: A JSON object containing the list of users if successful, None otherwise.
    """
    url = f"https://api.pingone.eu/v1/environments/{environment_id}/users"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in listing users: {e}")
        return None
    
def load_users():
    """
    Load users data from users.json.

    :return: Dictionary containing user data.
    """
    
    access_token = get_access_token()
    data = list_users(access_token, ENVIRONMENT_ID, limit=3)
    with open(user_data_path, "w") as file:
        json.dump(data, file)
    return data

def get_access_token():
    """
    Authenticate with PingOne and retrieve an access token.

    :return: A string containing the access token if successful, None otherwise.
    """
    url = "https://auth.pingone.eu/124e4bee-0fe0-440a-9ec0-960b1461585c/as/token"
    headers = {
        "Authorization": os.getenv('PINGONE_AUTH_TOKEN'),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error in getting access token: {e}")
        return None

def get_user_id_by_email(users_list, email):
    """
    Extract the user ID for a specific email address.

    :param users_list: The JSON object containing the list of users.
    :param email: The email address to search for.
    :return: The user ID if found, None otherwise.
    """
    for user in users_list.get("_embedded", {}).get("users", []):
        if user.get("email") == email:
            return user.get("id")
    return None

def list_users(access_token, environment_id, limit=3):
    """
    Fetch the list of users from PingOne.

    :param access_token: The access token for authentication.
    :param environment_id: The PingOne environment ID.
    :param limit: The number of users to retrieve (default is 3).
    :return: A JSON object containing the list of users if successful, None otherwise.
    """
    url = f"https://api.pingone.eu/v1/environments/{environment_id}/users"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in listing users: {e}")
        return None

def trigger_otp(access_token, email_id):
    """
    Trigger a one-time password (OTP) for a user via email.

    :param access_token: The access token for authentication.
    :param environment_id: The PingOne environment ID.
    :param user_id: The ID of the user to trigger the OTP for.
    :param email: The email address to send the OTP to.
    :return: A JSON object containing the OTP response if successful, None otherwise.
    """
    
    users_response = list_users(access_token, ENVIRONMENT_ID)
    user_id = get_user_id_by_email(users_response, email_id)

    url = f"https://auth.pingone.eu/{ENVIRONMENT_ID}/deviceAuthentications"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "user": {
            "id": user_id
        },
        "selectedDevice": {
            "oneTime": {
                "type": "EMAIL",
                "email": email_id
                # "email": 'srmanas0@gmail.com'
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response = response.json()
        authentication_id = response.get("id")
        if not authentication_id:
            print("Authentication ID not found in OTP response. Exiting.")
        return authentication_id
    except requests.exceptions.RequestException as e:
        print(f"Error in triggering OTP: {e}")
        return None

def verify_otp(access_token, authentication_id, otp):

    """
    Verify the OTP entered by the user.

    :param access_token: The access token for authentication.
    :param environment_id: The PingOne environment ID.
    :param authentication_id: The authentication ID from the OTP response.
    :param otp: The one-time password to verify.
    :return: A JSON object containing the verification response if successful, None otherwise.
    """
    url = f"https://auth.pingone.eu/{ENVIRONMENT_ID}/deviceAuthentications/{authentication_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.pingidentity.otp.check+json"
    }
    payload = {
        "otp": otp
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in verifying OTP: {e}")
        return None
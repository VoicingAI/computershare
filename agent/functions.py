import json
import os
import requests
from langchain_core.tools import tool
import random


user_data_path = '/home/ubuntu/VoicingAI-pingone/data/users.json'
ACCESS_TOKEN = None
EMAIL_ID = 'riwija2556@ahaks.com' 
# EMAIL_ID = 'manas.sr@voicing.ai'
ENVIRONMENT_ID = "124e4bee-0fe0-440a-9ec0-960b1461585c"  
USER_ID = "124e4bee-0fe0-440a-9ec0-960b1461585c"
PINGONE_AUTH_TOKEN = os.getenv('PINGONE_AUTH_TOKEN')  
ANSWERS = {
            "What is your mothers maiden name?": "Sheila",
            "What is four childhood sport?": "Curling"
        }

# Function 1: Load users
def load_users():
    """
    Load users data from users.json.

    :return: Dictionary containing user data.
    """
    with open(user_data_path, "r") as file:
        data = json.load(file)
        return data


@tool
def verify_user():
    """
    Verify if a user exists with the given email ID.

    :return: Dictionary indicating user validity.
    """
    global EMAIL_ID
    users = load_users()
    if any(user.get("email") == EMAIL_ID for user in users.get("_embedded", {}).get("users", [])):
        return 'User Valid'
    else:
        return 'User Invalid'


@tool
def get_security_questions():
    """
    Fetch security questions for the given email ID.

    :return: Dictionary of security questions.
    """
    global EMAIL_ID
    users = load_users()
    for user in users.get("_embedded", {}).get("users", []):
        if user.get("email") == EMAIL_ID:
            questions = user.get("security-questions", [])
            if questions:
                return {f'question{i+1}': question for i, question in enumerate(questions[0].keys())}
    return None


@tool
def verify_security_questions():
    """
    Verify the answers to security questions for the given email ID.

    :return: True if all answers are correct, False otherwise.
    """
    global EMAIL_ID, ANSWERS
    users = load_users()
    for user in users.get("_embedded", {}).get("users", []):
        if user.get("email") == EMAIL_ID:
            stored_questions = user.get("security-questions", [])
            if stored_questions:
                stored_answers = stored_questions[0]  # Extract the first dictionary
                for question, answer in ANSWERS.items():
                    if stored_answers.get(question) != answer:
                        return 'Invalid'
                return 'Valid'
    return False


@tool
def generate_otp():
    """
    Generate a 3-digit OTP.

    :return: The generated OTP as a string.
    """
    otp = random.randint(100,999)
    print(f"Generated OTP: {otp}")
    return otp

@tool
def verify_otp(expected_otp, provided_otp):
    """
    Verify if the provided OTP matches the expected OTP.

    :param expected_otp: The OTP that was generated.
    :param provided_otp: The OTP provided by the user.
    :return: True if the OTPs match, False otherwise.
    """
    if expected_otp == provided_otp:
        return 'OTP verified'
    else:
        return "OTP verification failed"


email_agent_tools = [verify_user]
securityqa_agent_tools = [get_security_questions, verify_security_questions]
otp_agent_tools = [generate_otp,verify_otp]

if __name__ == "__main__":
    otp = generate_otp()
    user_input = input("Enter the OTP: ")
    verify_otp(otp, user_input)
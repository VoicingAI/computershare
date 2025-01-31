from agent.utils import get_access_token, trigger_otp, verify_otp, load_users
from langchain_core.tools import tool

global EMAIL_ID
global authentication_id
global access_token
global users

users = load_users()

# Function 2: Verify user by email
@tool
def verify_user(email_id):
    """
    Verify if a user exists with the given email ID.

    :return: Dictionary indicating user validity.
    """
    global users
    global EMAIL_ID
    if any(user.get("email").lower() == email_id.lower() for user in users.get("_embedded", {}).get("users", [])):
        EMAIL_ID = email_id.lower()
        return 'User Valid'
    else:
        return 'User Invalid'


# Function 3: Get security questions
@tool
def get_security_questions():
    """
    Fetch security questions for the verified email ID.

    :return: Dictionary of security questions.
    """
    global users
    for user in users.get("_embedded", {}).get("users", []):
        if user.get("email") == EMAIL_ID:
            questions = user.get("security-questions", [])
            if questions:
                # return {f'question{i+1}': question for i, question in enumerate(questions[0].keys())}
                return {"question": list(questions[0].keys())[0]}
    return None

# Function 4: Verify security question answers
@tool
def verify_security_question(answer):
    """
    Verify the answer to the single security question for the given email ID.

    :param answer: Dictionary containing the question-answer pair to verify.
    :return: 'Answer Valid' if correct, otherwise 'Answer Invalid'.
    """
    global users
    for user in users.get("_embedded", {}).get("users", []):
        if user.get("email") == EMAIL_ID:
            stored_questions = user.get("security-questions", [])
            if stored_questions:
                stored_answers = stored_questions[0]  # Extract the first dictionary
                question = list(stored_answers.keys())[0]  # Fetch the same question
                if stored_answers.get(question).lower() == answer.get(question, "").lower():
                    return "Answer Valid"
                return "Answer Invalid"
    return "Answer Invalid"

# Function 5: OTP trigger
@tool
def process_otp():
    """
    Initiates the OTP verification process by triggering an OTP to be sent to the user's email.

    :return: A message confirming that the OTP has been sent, or an error message if the process fails.
    """
    # Step 1: Get access token
    global authentication_id
    global access_token
    global EMAIL_ID
    access_token = get_access_token()
    if not access_token:
        print("Failed to retrieve access token.")
        return

    # Step 2: Trigger OTP
    authentication_id = trigger_otp(access_token, EMAIL_ID)
    if not authentication_id:
        print("Failed to trigger OTP.")
        return

    return "OTP has been sent to the user's email."

@tool
def verify_processed_otp(otp):
    """
    Verify the OTP entered by the user.
    param: otp, The one-time password to verify.
    """
    global authentication_id
    global access_token
    
    print(access_token, authentication_id)
    verification_result = verify_otp(access_token, authentication_id, otp)
    if verification_result:
        return "OTP verified successfully."

    else:
        return "Failed to verify OTP."



email_agent_tools = [verify_user]
securityqa_agent_tools = [get_security_questions, verify_security_question]
otp_agent_tools = [process_otp, verify_processed_otp]


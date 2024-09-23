from flask_jwt_extended import create_access_token
from myproject.models import User

# List of users
users = [
    User(1, 'luis', 'pass'),
    User(2, 'nana', 'pass')
]

# Lookup tables for quick user retrieval
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

# Function to authenticate the user and generate an access token
def authenticate(username, password):
    # Get user by username
    user = username_table.get(username)
    
    # Check if user exists and password is correct
    if user and user.password == password:
        # Return JWT token if credentials are valid
        return create_access_token(identity=user.id)
    return None  # Return None if invalid credentials

# Identity function for retrieving user from JWT payload
def identity(payload):
    # Extract user id from the payload
    user_id = payload['identity']
    
    # Return the user object if found
    return userid_table.get(user_id, None)
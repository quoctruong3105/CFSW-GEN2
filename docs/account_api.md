# Auto-generated Documentation

## Function: getDBConnection

**Arguments:**

**Docstring:**

python
None


## Function: home

**Arguments:**

**Docstring:**

python
None


## Function: createUser

**Arguments:**

**Docstring:**

python
Create a new user in the account table.

This function handles a POST request to create a new user. It expects
the request payload to contain 'username', 'password', and optionally 'role'.
The username and password are required fields. If either is missing,
it returns a 400 response with an error message.

The function connects to the PostgreSQL database to insert the new user's
information, including their username, password, and role. It also initializes
the 'last_login' and 'last_logout' fields as NULL.

Upon successful creation of the user, it returns the user's ID along with
a success message and a 201 status code. If a database error occurs,
it catches the error and returns a 500 response.

Parameters:
- The request must include a JSON body with 'username', 'password', and 'role'.

Returns:
- On success: a JSON response with a message and the user ID, status code 201.
- On failure (missing fields): a JSON error message with status code 400.
- On database error: a JSON error message with status code 500.


## Function: changePassword

**Arguments:**

**Docstring:**

python
Change the user's password.

This function handles a PUT request to change the user's password. It expects
the request payload to contain 'username', 'oldPassword', and 'newPassword'.
All three fields are required. If any of these are missing, the function returns
a 400 response with an error message.

Parameters:
- The request must include a JSON body with 'username', 'oldPassword', and 'newPassword'.

Returns:
- On success: a JSON response with a message, status code 200.
- On failure (missing fields): a JSON error message with status code 400.
- On failure (user not found): a JSON error message with status code 404.
- On failure (admin trying to change password): a JSON error message with status code 403.
- On failure (incorrect old password): a JSON error message with status code 401.
- On database error: a JSON error message with status code 500.


## Function: deleteUser

**Arguments:**

**Docstring:**

python
Delete a user from the account table.

This function handles a DELETE request to delete a user. It expects
the request payload to contain 'username' and 'password'. Both fields
are required. If either is missing, the function returns a 400 response
with an error message.

Parameters:
- The request must include a JSON body with 'username' and 'password'.

Returns:
- On success: a JSON response with a message, status code 200.
- On failure (missing fields): a JSON error message with status code 400.
- On failure (user not found): a JSON error message with status code 404.
- On failure (admin account cannot be deleted): a JSON error message with status code 403.
- On failure (incorrect password): a JSON error message with status code 401.
- On database error: a JSON error message with status code 500.


## Function: getLastLogin

**Arguments:** username

**Docstring:**

python
Retrieve the last login time of a user.

This function handles a GET request to fetch the last login time for a user
based on their username. The username is passed as a path parameter.
If the username is not found in the database, it returns a 404 response.

Parameters:
- username (string): The username passed as a URL parameter.

Returns:
- On success: a JSON response with the last login timestamp, status code 200.
- On failure (user not found): a JSON error message with status code 404.
- On database error: a JSON error message with status code 500.


## Function: getLastLogout

**Arguments:** username

**Docstring:**

python
Retrieve the last logout time of a user.

This function handles a GET request to fetch the last logout time for a user
based on their username. The username is passed as a path parameter.
If the username is not found in the database, it returns a 404 response.

Parameters:
- username (string): The username passed as a URL parameter.

Returns:
- On success: a JSON response with the username and the last logout timestamp, status code 200.
- On failure (user not found): a JSON error message with status code 404.
- On database error: a JSON error message with status code 500.


## Function: verifyLogin

**Arguments:**

**Docstring:**

python
Verify user login credentials.

This function handles a POST request to verify a user's login credentials.
It expects the request payload to contain 'username' and 'password'.
Both fields are required. If either is missing, it returns a 400 response
with an error message.

Parameters:
- The request must include a JSON body with 'username' and 'password'.

Returns:
- On success: a JSON response with a success message, status code 200.
- On failure (missing fields): a JSON error message with status code 400.
- On failure (user not found): a JSON error message with status code 404.
- On failure (incorrect password): a JSON error message with status code 401.
- On database error: a JSON error message with status code 500.



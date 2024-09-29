*** Settings ***
Library  RequestsLibrary
Library  Collections

*** Variables ***
${BASE_URL}    http://account:5000
${EXPECTED_MESSAGE_CREATE_USER}    User created successfully
${EXPECTED_MESSAGE_CHANGE_PASS}    Password changed successfully
${EXPECTED_MESSAGE_DELETE_USER}    User deleted successfully
${USERNAME}          john_doe
${LAST_LOGIN_AD}     2024-09-18 09:00:00
${LAST_LOGOUT_AD}    2024-09-18 17:00:00
${EXPECTED_MESSAGE_VERIFY_LOGIN}    Login successful


*** Test Cases ***
Test Home Page
    [Documentation]  Verify that the home page returns the correct message.

    ${response}=  GET  ${BASE_URL}/
    Should Be Equal As Numbers  ${response.status_code}  200
    ${actual_content}=    Set Variable     ${response.content.decode('utf-8')}
    Should Be Equal  ${actual_content}  Hello from Account service

Test Create User
    [Documentation]  Verify that the new user has been added successfully.

    # Prepare JSON payload and headers
    &{payload}=    Create Dictionary    username=vu    password=123    role=CEO
    &{headers}=    Create Dictionary    Content-Type=application/json

    # Send POST request
    ${response}=    POST    ${BASE_URL}/create_user    headers=&{headers}    json=${payload}

    # Check if the response status code is 201 (created)
    Should Be Equal As Numbers    ${response.status_code}    201

    # Parse and validate JSON response
    ${response_json}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response_json['message']}    ${EXPECTED_MESSAGE_CREATE_USER}

    Log Status and JSON    ${response}

Test Verify Login
    [Documentation]    This test case checks the verifyLogin API.


    ${payload}=          Create Dictionary    username=vu    password=123
    ${response}=      POST    ${BASE_URL}/verifyLogin    json=${payload}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${response_json}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response_json['message']}    ${EXPECTED_MESSAGE_VERIFY_LOGIN}

    Log Status and JSON    ${response}

Test Change Password
    [Documentation]    Test successful password change.

    ${payload}=    Create Dictionary    username=vu    old_password=123    new_password=321

    ${response}=    PUT    ${BASE_URL}/change_password    json=${payload}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${response_json}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response_json['message']}    ${EXPECTED_MESSAGE_CHANGE_PASS}

    Log Status and JSON    ${response}

Test Delete User
    [Documentation]    Test successful user deletion with valid credentials.

    ${payload}=    Create Dictionary    username=vu    password=321

    ${response}=    DELETE    ${BASE_URL}/delete_user    json=${payload}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${response_json}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response_json['message']}    ${EXPECTED_MESSAGE_DELETE_USER}

    Log Status and JSON    ${response}

Test Get Last Login
    [Documentation]    This test case checks the getlastlogin API.

    ${response}=      GET     ${BASE_URL}/getlastlogin/${USERNAME}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${response_json}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response_json['last_login']}    ${LAST_LOGIN_AD}

    Log Status and JSON    ${response}

Test Get Last Logout
    [Documentation]    This test case checks the getlastlogout API.

    ${response}=      GET     ${BASE_URL}/getlastlogout/${USERNAME}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${response_json}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${response_json['last_logout']}    ${LAST_LOGOUT_AD}

    Log Status and JSON    ${response}


*** Keywords ***
Log Status and JSON
    [Arguments]    ${response}

    # Convert the response JSON to a string for logging
    ${response_json}=    Convert To String    ${response.json()}
    # Log response details for debugging
    Log To Console    Status Code: ${response.status_code}
    Log To Console    Response JSON: ${response_json}

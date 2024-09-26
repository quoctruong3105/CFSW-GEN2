*** Settings ***
Library  RequestsLibrary
Library  Collections

*** Variables ***
${BASE_URL}    http://localhost:5000
${EXPECTED_MESSAGE}    User created successfully
${EXPECTED_USER_ID}    4

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
    Should Be Equal As Strings    ${response_json['message']}    ${EXPECTED_MESSAGE}

    # Log response details for debugging
    Log To Console    Status Code: ${response.status_code}
    Log To Console    Response JSON: ${response_json}
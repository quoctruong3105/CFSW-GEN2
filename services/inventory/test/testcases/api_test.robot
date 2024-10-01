*** Settings ***
Library  RequestsLibrary
Library  Collections

*** Variables ***
${BASE_URL}    http://inventory:5000

*** Test Cases ***
Test Home Page
    [Documentation]  Verify that the home page returns the correct message.
    ${response}=  GET  ${BASE_URL}  /
    Should Be Equal As Numbers  ${response.status_code}  200
    ${actual_content}=    Set Variable     ${response.content.decode('utf-8')}
    Should Be Equal  ${actual_content}  Hello from Inventory service

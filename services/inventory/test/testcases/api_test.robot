*** Settings ***
Library  RequestsLibrary
Library  Collections

*** Variables ***
${BASE_URL}    http://inventory:5000
${CAKE_NAME}    Macaron
${TOPPING_NAME}    Kem
${SOLD_UNITS}     ${5}
${EXPECTED_MESSAGE_QUANTITY}    Quantity updated successfully

*** Test Cases ***
Test Home Page
    [Documentation]  Verify that the home page returns the correct message.

    ${response}=  GET  ${BASE_URL}  /
    Should Be Equal As Numbers  ${response.status_code}  200
    ${actual_content}=    Set Variable     ${response.content.decode('utf-8')}
    Should Be Equal  ${actual_content}  Hello from Inventory service

Test Get List of Cakes
    [Documentation]    Verify that we can retrieve the list of cakes.

    ${response}=    GET    ${BASE_URL}/getListCake

    Should Be Equal As Numbers    ${response.status_code}    200

    Log Status and JSON    ${response}

Test Update Cake Quantity
    [Documentation]    Verify that we can update the quantity of a specific cake.

    ${payload}=    Create Dictionary    cake=${CAKE_NAME}    sold_unit=${SOLD_UNITS}
    ${response}=    POST    ${BASE_URL}/updateCakeQuantity    json=${payload}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${response_json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Value    ${response.json()}    ${EXPECTED_MESSAGE_QUANTITY}

    Log Status and JSON    ${response}

Test Get List of Toppings
    [Documentation]    Verify that we can retrieve the list of toppings.

    ${response}=    GET    ${BASE_URL}/getListTopping
    Should Be Equal As Numbers    ${response.status_code}    200

    Log Status and JSON    ${response}

Test Update Topping Quantity
    [Documentation]    Verify that we can update the quantity of a specific topping.

    ${payload}=    Create Dictionary    topping=${TOPPING_NAME}    sold_unit=${SOLD_UNITS}
    ${response}=    POST    ${BASE_URL}/updateToppingQuantity    json=${payload}

    Should Be Equal As Numbers    ${response.status_code}    200

    Dictionary Should Contain Value    ${response.json()}    ${EXPECTED_MESSAGE_QUANTITY}

    Log Status and JSON    ${response}


*** Keywords ***
Log Status and JSON
    [Arguments]    ${response}

    # Convert the response JSON to a string for logging
    ${response_json}=    Convert To String    ${response.json()}
    # Log response details for debugging
    Log To Console    Status Code: ${response.status_code}
    Log To Console    Response JSON: ${response_json}
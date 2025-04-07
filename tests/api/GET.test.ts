import { APIActions } from '@lib/APIActions';
import { test, expect } from '@playwright/test';

const apiActions = new APIActions();

// test(`getUsers`, { tag: '@API'}, async ({ request }) => {
//     const response = await request.get(`/api/users?per_page=1`);
//     await apiActions.verifyStatusCode(response);
//
//     //* Body Response Params and Body Response Headers are stored in single text file separated by #
//     const responseBodyParams = (await apiActions.readValuesFromTextFile(`getUsers`)).split(`#`)[0];
//     await apiActions.verifyResponseBody(responseBodyParams, await response.json(), `Response Body`);
//
//     const responseBodyHeaders = (await apiActions.readValuesFromTextFile(`getUsers`)).split(`#`)[1];
//     await apiActions.verifyResponseHeader(responseBodyHeaders, response.headersArray(), `Response Headers`);
// });

test(`getAllProducts`, { tag: '@API' }, async ({ request }) => {
    // Make the request
    const response = await request.get(`/api/productsList`);
    
    // Verify status code using existing helper
    await apiActions.verifyStatusCode(response);
    
    // Get response body
    const responseBody = await response.json();
    const responseBodyHeaders = (await apiActions.readValuesFromTextFile(`getProducts`)).split(`#`)[1];

    // В начале теста добавьте:
    console.log('Response headers:', response.headersArray());
    console.log('Expected headers:', responseBodyHeaders);
    
    // Get expected response parameters and verify body
    const responseBodyParams = (await apiActions.readValuesFromTextFile(`getProducts`)).split(`#`)[0];
    await apiActions.verifyResponseBody(responseBodyParams, responseBody, `Response Body`);

    // Additional schema validations
    expect(Array.isArray(responseBody.products)).toBeTruthy();
    for (const product of responseBody.products) {
        expect(product).toMatchObject({
            id: expect.any(Number),
            name: expect.any(String),
            price: expect.stringMatching(/^Rs\. \d+$/),
            brand: expect.any(String),
            category: {
                usertype: {
                    usertype: expect.stringMatching(/^(Women|Men|Kids)$/)
                },
                category: expect.any(String)
            }
        });
    }

    // Get and verify headers
    // const responseBodyHeaders = (await apiActions.readValuesFromTextFile(`getProducts`)).split(`#`)[1];
    await apiActions.verifyResponseHeader(responseBodyHeaders, response.headersArray(), `Response Headers`);
});

// Negative test case
test(`getAllProducts - invalid endpoint`, { tag: '@API' }, async ({ request }) => {
    const response = await request.get(`/api/productsListInvalid`);
    expect(response.status()).toBe(404);
});



//* In Case you application has token system, Please use the below code

// test(`@API getUsersToken`, async ({ playwright, baseURL }) => {
//     const apiContext = await playwright.request.newContext({
//         baseURL: baseURL,
//         extraHTTPHeaders: {
//             'Authorization': `Your App Token`
//         }
//     });
//     const response = await apiContext.get(`/api/users?per_page=1`);
//     await apiActions.verifyStatusCode(response.status(), 200);

//     //* Body Response Params and Body Response Headers are stored in single text file separated by #
//     const responseBodyParams = (await apiActions.readValuesFromTextFile(`getUsers`)).split(`#`)[0];
//     await apiActions.verifyResponseBody(responseBodyParams, await response.json(), `Response Body`);

//     const responseBodyHeaders = (await apiActions.readValuesFromTextFile(`getUsers`)).split(`#`)[1];
//     await apiActions.verifyResponseHeader(responseBodyHeaders, response.headersArray(), `Response Headers`);
// });




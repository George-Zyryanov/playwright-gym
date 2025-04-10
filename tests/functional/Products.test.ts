import test from '@lib/BaseTest'
import {expect} from "@playwright/test";
import { createTestMetadata } from '@lib/TestMetadata';
import { ProductSteps } from '../steps/ProductSteps';

test('Verify Products Page', createTestMetadata({
    testId: 'TC001',
    testName: 'Verify Products Search Functionality',
    description: 'Verifies that product search returns correct results and displays them properly',
    linkInTestManagementSys: 'https://testmanagement.example.com/testcase/TC001',
    priority: 'P1',
    author: 'George Zyryanov',
    linkToJiraTicket: 'https://jira.example.com/browse/JIRA-123',
    pageUnderTest: 'ProductsPage',
    featureUnderTest: 'ProductSearch'
}), async ({productsPage, mainPage}) =>{
    // Method 1: Individual steps approach - clear and readable
    
    // Navigate to products page
    await ProductSteps.navigateToProductsPage(mainPage);
    
    // Verify products page loaded correctly
    await ProductSteps.verifyProductsPageLoaded(productsPage);
    
    // Search for product
    const searchTerm = "WRONG PRODUCT";
    await ProductSteps.searchForProduct(productsPage, searchTerm);
    
    // Verify search results
    await ProductSteps.verifySearchResults(productsPage, searchTerm);
    
    // Method 2: Using the combined workflow (commented out)
    // This single line would replace all the above steps
    // 
    // const searchTerm = "Frozen Tops For Kids";
    // await ProductSteps.searchAndVerifyProduct(mainPage, productsPage, searchTerm);
})

// export npm_config_ENV="qa"
// npm run test:single tests/functional/Products.test.ts 
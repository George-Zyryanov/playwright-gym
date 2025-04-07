import test from '@lib/BaseTest'
import {expect} from "@playwright/test";

test('Verify Products Page', {tag: '@Smoke'}, async ({productsPage, mainPage}) =>{
    await mainPage.navigateToURL();
    await mainPage.clickOnProductsLink();

    // Verify that Product Page is loaded
    await expect(productsPage.isProductPage()).toBeTruthy();
    await expect(productsPage.isAllProductsTextVisible()).toBeTruthy();

    await productsPage.searchInput.fill("Frozen Tops For Kids")
    await productsPage.searchButton.click();

    // Verify that Search Results Text is visible
    await expect(productsPage.getSearchProductsText()).toBeTruthy()

    // Only 1 product should be visible
    await expect(productsPage.singleProduct.getByText("Frozen Tops For Kids")).toHaveCount(1)
})

// export npm_config_ENV="qa"
// npm run test:single tests/functional/Products.test.ts
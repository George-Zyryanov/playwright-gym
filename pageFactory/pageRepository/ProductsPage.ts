import {BrowserContext, expect, Locator, Page} from "@playwright/test";
import {WebActions} from "@lib/WebActions";

let webActions : WebActions;

export class ProductsPage {
    readonly page: Page;
    readonly context: BrowserContext;
    readonly allProductsText: Locator;
    readonly searchedProductsText: Locator;
    readonly searchInput: Locator;
    readonly searchButton: Locator;
    readonly singleProduct: Locator;

    constructor(page: Page, context: BrowserContext) {
        this.page = page;
        this.context = context;
        webActions = new WebActions(this.page, this.context);
        this.allProductsText = page.getByRole("heading", {name: "All Products"});
        this.searchedProductsText = page.getByRole("heading", {name: "Searched Products"});
        this.searchInput = page.locator("input#search_product");
        this.searchButton = page.locator("button#submit_search");
        this.singleProduct = page.locator("div.productinfo");
    }

    async isProductPage(): Promise<boolean> {
        return this.page.url().includes("/products");
    }

    async isAllProductsTextVisible(): Promise<boolean> {
        return await this.allProductsText.isVisible();
    }

    async getSearchProductsText(): Promise<boolean> {
        return await this.searchedProductsText.isVisible()
    }

    async searchForProduct(productName : string): Promise<void> {
        await this.searchInput.fill(productName);
        await this.searchButton.click();
    }
}
import { Page, BrowserContext, Locator } from '@playwright/test'
import { WebActions } from "@lib/WebActions";

let webActions: WebActions;

export class MainPage {
    readonly page: Page;
    readonly context: BrowserContext;
    readonly productsLink: Locator;
    readonly dialogWindowConsentButton: Locator;

    constructor(page: Page, context: BrowserContext) {
        this.page = page;
        this.context = context;
        this.dialogWindowConsentButton = page.getByRole("button", {name: "Consent"})
        this.productsLink = page.getByRole("link", {name: "Products"})
        webActions = new WebActions(this.page, this.context);
    }

    async clickOnProductsLink(): Promise<void> {
        await this.productsLink.click();
    }

    async navigateToURL(): Promise<void> {
        await this.page.goto("/");
        try {
            await this.dialogWindowConsentButton.click()

        } catch (Error) {
            console.log("The modal window was not present. Error --> ",Error);
        }
    }
}
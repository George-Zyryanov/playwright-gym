# Playwright Test Steps Best Practices

This guide outlines best practices for creating readable, maintainable test steps in Playwright tests. Well-structured test steps improve test readability, debugging efficiency, and provide clear reports and traces.

## Why Use Test Steps?

Test steps in Playwright:

1. **Improve Readability**: Make tests more readable for both technical and non-technical stakeholders
2. **Enhance Reports**: Create detailed, structured reports that reflect the user flow
3. **Simplify Debugging**: When tests fail, quickly identify which step failed
4. **Document Behavior**: Effectively document the expected application behavior

## Basic Test Steps Structure

Playwright provides the `test.step()` API for creating named steps. Each step should:

1. Have a descriptive name that reflects the user action or verification
2. Contain a single logical action or closely related set of actions
3. Include appropriate verifications where applicable

```typescript
await test.step('Navigate to login page', async () => {
  await page.goto('/login');
  await expect(page).toHaveURL(/.*login/);
});

await test.step('Login with valid credentials', async () => {
  await page.getByLabel('Username').fill('testuser');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page.getByText('Welcome')).toBeVisible();
});
```

## Best Practices for Step Names

Step names should:

1. **Be Action-Oriented**: Use verbs that describe the action being performed
   - ✅ "Navigate to login page"
   - ❌ "Login page"

2. **Be Specific and Descriptive**: Provide enough context to understand the step
   - ✅ "Add 'JavaScript Learning' book to cart"
   - ❌ "Add item"

3. **Use Dynamic Content When Relevant**: Include test data in step names for clarity
   - ✅ `Search for product: "${searchTerm}"`
   - ❌ "Search for product"

4. **Maintain Consistent Style**: Use the same style throughout the test suite
   - Either use sentence case, title case, or other consistent formatting
   - Keep terminology consistent across similar actions

## Organizing Test Steps

### Logical Grouping

Group steps logically to reflect user workflows:

```typescript
// Navigation steps
await test.step('Navigate to application', async () => { /* ... */ });

// Authentication steps
await test.step('Login as admin user', async () => { /* ... */ });

// Action steps
await test.step('Create new product', async () => { /* ... */ });

// Verification steps
await test.step('Verify product was created successfully', async () => { /* ... */ });
```

### Nested Steps

For complex flows, use nested steps to create a hierarchy:

```typescript
await test.step('Complete checkout process', async () => {
  await test.step('Fill shipping information', async () => { /* ... */ });
  await test.step('Select payment method', async () => { /* ... */ });
  await test.step('Confirm order', async () => { /* ... */ });
});
```

## Reusable Step Patterns

For better maintainability, create reusable step functions:

```typescript
// In a shared file like TestSteps.ts
export class NavigationSteps {
  static async navigateToPage(page, url, pageTitle) {
    await test.step(`Navigate to ${pageTitle} page`, async () => {
      await page.goto(url);
      await expect(page).toHaveTitle(new RegExp(pageTitle, 'i'));
    });
  }
}

// In your test
await NavigationSteps.navigateToPage(page, '/login', 'Login');
```

## Verification Steps

Always include verifications within steps to ensure actions completed successfully:

```typescript
await test.step('Login to application', async () => {
  await page.getByLabel('Username').fill('testuser');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Login' }).click();
  
  // ✅ Always include verification within the step
  await expect(page.getByText('Welcome')).toBeVisible();
});
```

## Test Step Integration with Test Metadata

When using test metadata as in our framework, combine them effectively:

```typescript
test('User can add product to cart', createTestMetadata({
  testId: 'SHOP001',
  testName: 'Add product to shopping cart',
  description: 'Verifies users can add products to their shopping cart',
  priority: 'P1',
  author: 'Test Engineer',
  pageUnderTest: 'ProductsPage',
  featureUnderTest: 'ShoppingCart'
}), async ({ page }) => {
  await test.step('Navigate to products page', async () => { /* ... */ });
  await test.step('Select product category', async () => { /* ... */ });
  await test.step('Add product to cart', async () => { /* ... */ });
  await test.step('Verify product is in cart', async () => { /* ... */ });
});
```

## Benefits in Reports and Traces

With well-structured steps:

1. **HTML Reports**: Reports will display a clear hierarchy of steps, making it easy to understand the test flow and identify failures
2. **Trace Viewer**: The timeline in the trace viewer will show steps as named groups, making it easier to navigate complex traces
3. **CI/CD Integration**: Step data can be parsed and used in CI/CD systems for better reporting

## Common Anti-Patterns to Avoid

1. **Too Granular**: Avoid making every single action a separate step
   - ❌ `await test.step('Click login button', async () => { await page.click('button'); });`

2. **Too Broad**: Avoid putting too many unrelated actions in a single step
   - ❌ `await test.step('Setup test', async () => { /* 100 lines of different actions */ });`

3. **Misleading Names**: Ensure step names accurately reflect the actions
   - ❌ `await test.step('Verify login', async () => { /* Code that adds products to cart */ });`

4. **Missing Verifications**: Don't create steps that lack appropriate assertions
   - ❌ `await test.step('Login successfully', async () => { /* Only actions, no verifications */ });`

## Examples

Here are some examples of well-structured test steps:

### Authentication Flow

```typescript
await test.step('Navigate to login page', async () => {
  await page.goto('/login');
  await expect(page).toHaveURL(/.*login/);
});

await test.step('Attempt login with invalid credentials', async () => {
  await page.getByLabel('Username').fill('wronguser');
  await page.getByLabel('Password').fill('wrongpass');
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page.getByText('Invalid username or password')).toBeVisible();
});

await test.step('Login with valid credentials', async () => {
  await page.getByLabel('Username').clear();
  await page.getByLabel('Password').clear();
  await page.getByLabel('Username').fill('testuser');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page.getByText('Welcome')).toBeVisible();
});
```

### Shopping Cart Flow

```typescript
await test.step('Search for a product', async () => {
  const searchTerm = 'Wireless Headphones';
  await page.getByPlaceholder('Search').fill(searchTerm);
  await page.getByRole('button', { name: 'Search' }).click();
  await expect(page.getByText('Search Results')).toBeVisible();
});

await test.step('Add product to cart', async () => {
  const productName = 'Noise Cancelling Headphones X5';
  await page.getByText(productName).click();
  await page.getByRole('button', { name: 'Add to Cart' }).click();
  await expect(page.getByText('Added to Cart')).toBeVisible();
});

await test.step('Proceed to checkout', async () => {
  await page.getByRole('link', { name: 'Cart' }).click();
  await expect(page.getByText('Shopping Cart')).toBeVisible();
  await page.getByRole('button', { name: 'Checkout' }).click();
  await expect(page.getByText('Shipping Information')).toBeVisible();
});
```

## Conclusion

Following these best practices for test steps in Playwright tests will result in more readable, maintainable tests that are easier to debug and provide clearer reporting. Consistent step naming and organization help everyone understand test flows and expected application behavior. 
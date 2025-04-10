# Test Steps

This directory contains reusable test step implementations organized by page or feature. These step files encapsulate common interactions with the application to improve test readability and maintainability.

## Purpose

Test steps provide several benefits:
- Improve test readability by using descriptive step names
- Reduce code duplication across test files
- Create a single point of maintenance when page objects change
- Make test flows visible in reports and traces

## Usage

Import step classes into your test files:

```typescript
// Option 1: Import specific step classes
import { ProductSteps } from '../steps/ProductSteps';

// Option 2: Import from index file when multiple step classes are needed
import { ProductSteps, LoginSteps } from '../steps';

// Use steps in tests
await ProductSteps.navigateToProductsPage(mainPage);
await ProductSteps.searchForProduct(productsPage, "Product Name");
```

## Best Practices

When creating or modifying step files:

1. **Keep steps focused** - Each step should perform a single logical action
2. **Include verifications** - Steps should validate that actions completed successfully
3. **Use descriptive names** - Step methods should clearly indicate what they do
4. **Keep page-specific steps in dedicated files** - Organize by page/feature
5. **Consider step granularity** - Provide both granular steps and composite workflows
6. **Make step parameters clear** - Use specific types and meaningful parameter names
7. **Document steps** - Use JSDoc comments to describe purpose and parameters

## Structure

- Each step file should focus on a specific page or feature
- Step files should be named after the page they interact with (e.g., ProductSteps.ts)
- Step classes should be named similarly (e.g., ProductSteps)
- Related steps should be grouped in the same class
- Complex workflows can combine multiple granular steps 
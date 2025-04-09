/**
 * TestMetadata utility for standardizing test metadata across the project
 */

/**
 * Priority levels for tests
 */
export type TestPriority = 'P1' | 'P2' | 'P3' | 'P4';

/**
 * Test metadata interface defining all possible metadata fields
 */
export interface TestMetadata {
  /**
   * Unique test identifier
   */
  testId: string;

  /**
   * Human-readable test name
   */
  testName: string;

  /**
   * Detailed test description
   */
  description: string;

  /**
   * Link to the test in the test management system
   */
  linkInTestManagementSys?: string;

  /**
   * Test priority (P1-P4)
   */
  priority: TestPriority;

  /**
   * Test author name
   */
  author: string;

  /**
   * URL link to associated Jira ticket
   */
  linkToJiraTicket?: string;

  /**
   * Page being tested
   */
  pageUnderTest: string;

  /**
   * Feature being tested
   */
  featureUnderTest: string;
}

/**
 * Creates metadata object with tags and annotations for Playwright test
 * @param metadata Test metadata
 * @returns Object with tag and annotation fields for Playwright test
 */
export function createTestMetadata(metadata: TestMetadata) {
  return {
    tag: [
      `@${metadata.testId}`,
      `@${metadata.priority}`,
      `@${metadata.pageUnderTest}`,
      `@${metadata.featureUnderTest}`
    ],
    annotation: [
      { type: 'Test ID', description: metadata.testId },
      { type: 'Test Name', description: metadata.testName },
      { type: 'Description', description: metadata.description },
      { type: 'Priority', description: metadata.priority },
      { type: 'Author', description: metadata.author },
      { type: 'Page', description: metadata.pageUnderTest },
      { type: 'Feature', description: metadata.featureUnderTest },
      ...(metadata.linkInTestManagementSys ? [{ type: 'Link', description: metadata.linkInTestManagementSys }] : []),
      ...(metadata.linkToJiraTicket ? [{ type: 'Jira Ticket', description: metadata.linkToJiraTicket }] : [])
    ]
  };
} 
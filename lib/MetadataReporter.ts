import { Reporter, TestCase, TestResult } from '@playwright/test/reporter';

/**
 * Custom reporter that displays test metadata in console output
 */
class MetadataReporter implements Reporter {
  onTestEnd(test: TestCase, result: TestResult) {
    // Only log for completed tests
    if (result.status) {
      // Extract metadata from test
      const tags = test.tags || [];
      const annotations = test.annotations || [];
      
      // Create a formatted output
      const status = this.getStatusSymbol(result.status);
      const testId = this.findAnnotationValue(annotations, 'Test ID') || this.findTagValue(tags, '@TC');
      const priority = this.findAnnotationValue(annotations, 'Priority') || this.findTagValue(tags, '@P');
      const author = this.findAnnotationValue(annotations, 'Author') || 'Unknown';
      const page = this.findAnnotationValue(annotations, 'Page') || this.findTagValue(tags, '@') || 'Unknown';
      const feature = this.findAnnotationValue(annotations, 'Feature') || 'Unknown';
      const jiraTicket = this.findAnnotationValue(annotations, 'Jira Ticket');
      
      // Log formatted metadata
      console.log(`${status} [${testId}][${priority}] ${test.title}`);
      console.log(`   Page: ${page} | Feature: ${feature} | Author: ${author}${jiraTicket ? ` | Jira: ${jiraTicket}` : ''}`);
      
      // If test failed, add separator line for better readability
      if (result.status === 'failed') {
        console.log('   ---');
      }
    }
  }

  /**
   * Get a symbol to represent test status
   */
  private getStatusSymbol(status: string): string {
    switch(status) {
      case 'passed': return '✅';
      case 'failed': return '❌';
      case 'timedOut': return '⏱️';
      case 'skipped': return '⏭️';
      default: return '❓';
    }
  }

  /**
   * Find value from annotations by type
   */
  private findAnnotationValue(annotations: any[], type: string): string | undefined {
    const annotation = annotations.find(a => a.type === type);
    return annotation?.description;
  }

  /**
   * Find tag value by prefix
   */
  private findTagValue(tags: string[], prefix: string): string | undefined {
    const tag = tags.find(t => t.startsWith(prefix));
    return tag ? tag.substring(prefix.length) : undefined;
  }
}

export default MetadataReporter; 
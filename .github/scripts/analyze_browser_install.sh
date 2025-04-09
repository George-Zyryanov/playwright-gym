#!/bin/bash

# Script to analyze Playwright browser installation performance

echo "===== Playwright Browser Installation Analysis ====="
echo ""

# Check cache directory existence
if [ -d ~/.cache/ms-playwright ]; then
  CACHE_SIZE=$(du -sh ~/.cache/ms-playwright | cut -f1)
  BROWSER_COUNT=$(find ~/.cache/ms-playwright -name "chrome-*" -o -name "firefox-*" -o -name "webkit-*" | wc -l)
  
  echo "Cache status:"
  echo "- Cache directory: EXISTS"
  echo "- Cache size: $CACHE_SIZE"
  echo "- Browser binaries found: $BROWSER_COUNT"
  
  # List browser versions
  echo "- Installed browsers:"
  find ~/.cache/ms-playwright -name "chrome-*" -o -name "firefox-*" -o -name "webkit-*" | while read browser; do
    echo "  - $(basename $browser)"
  done
  
  # Detailed cache structure - this helps debug why cache might not be working
  echo ""
  echo "Cache directory structure (top level):"
  ls -la ~/.cache/ms-playwright/
  
  echo ""
  echo "Browser directory permissions:"
  find ~/.cache/ms-playwright -name "chrome-*" -type d -exec ls -ld {} \;
  
  # Check if Chrome is actually installed
  if which google-chrome &>/dev/null; then
    echo ""
    echo "Google Chrome version:"
    google-chrome --version
  else
    echo ""
    echo "Google Chrome is NOT installed in system path"
  fi
  
  # Check Playwright browser drivers
  echo ""
  echo "Playwright installed browser paths:"
  if command -v npx &>/dev/null; then
    npx playwright --version
    npx playwright install chrome --dry-run 2>&1 | grep -i "browser download"
  fi
else
  echo "Cache status:"
  echo "- Cache directory: NOT FOUND"
  echo "- Browsers will be installed from scratch"
fi

echo ""
echo "==== System Information ===="
echo "- OS: $(uname -s)"
echo "- Architecture: $(uname -m)"
echo "- Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "- Disk space: $(df -h / | grep / | awk '{print $4}') available"

echo ""
echo "==== Recommendations ===="
echo "1. Use '--with-deps' flag for fresh installs to reduce roundtrips"
echo "2. Use PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 when deps are needed but browser is already cached"
echo "3. Use 'npx playwright install-deps chrome --dry-run' to check if deps are already installed"
echo "4. Verify your cache keys are correctly capturing browser versions"
echo "5. Use '--dry-run' to avoid unnecessary dependency installation"
echo "6. Ensure cache directory has correct permissions (755) for GitHub Actions"
echo "7. Include playwright.config.ts/js in your cache key to catch browser version changes"
echo ""
echo "===== Analysis Complete =====" 
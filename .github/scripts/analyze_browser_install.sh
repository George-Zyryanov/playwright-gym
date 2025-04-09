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
echo ""
echo "===== Analysis Complete =====" 
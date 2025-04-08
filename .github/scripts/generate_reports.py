#!/usr/bin/env python3
"""
GitHub Pages Report Generator for Playwright Tests

This script generates a static HTML page for displaying test report history.
It maintains a history of the last 10 test runs and provides status indicators.

Usage:
  python generate_reports.py

Required Environment Variables:
  - GITHUB_SHA: The commit SHA
  - COMMIT_MESSAGE: The commit message
  - GITHUB_RUN_NUMBER: The GitHub Actions run number
  - GITHUB_RUN_ID: The GitHub Actions run ID
  - BUILD_STATUS: The build job status (success, failure, etc.)
  - BUILD_DURATION: (Optional) The build duration in seconds
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from jinja2 import Template
import glob
import sys

def main():
    # Get commit info from environment variables
    commit_sha = os.environ.get('GITHUB_SHA')
    commit_message = os.environ.get('COMMIT_MESSAGE')
    
    try:
        run_number = int(os.environ.get('GITHUB_RUN_NUMBER', '0'))
    except ValueError:
        print(f"Error: Invalid run number: {os.environ.get('GITHUB_RUN_NUMBER')}")
        run_number = 0
    
    run_id = os.environ.get('GITHUB_RUN_ID')
    
    # Get build job status - convert to lowercase for consistency
    build_status = os.environ.get('BUILD_STATUS', '').lower()
    
    # Get build duration if available (in seconds)
    try:
        build_duration_seconds = int(os.environ.get('BUILD_DURATION', '0'))
        # Format duration in a human-readable format
        if build_duration_seconds > 0:
            duration = str(timedelta(seconds=build_duration_seconds))
            # Remove microseconds if present
            if '.' in duration:
                duration = duration.split('.')[0]
        else:
            duration = "Unknown"
    except ValueError:
        print(f"Error: Invalid build duration: {os.environ.get('BUILD_DURATION')}")
        duration = "Unknown"
    
    print(f"Build duration: {duration}")

    # Map GitHub Actions status to our status values
    status_map = {
        'success': 'success',
        'failure': 'failure',
        'cancelled': 'unknown',
        'skipped': 'unknown'
    }
    status = status_map.get(build_status, 'unknown')
    
    print(f"Processing report for commit: {commit_sha}")
    print(f"Run number: {run_number}")
    print(f"Build status: {build_status} -> {status}")
    
    # Create directory for this run
    report_dir = f'reports/{commit_sha}'
    os.makedirs(report_dir, exist_ok=True)
    
    # Check if html-report exists and has content
    if os.path.exists('html-report'):
        # List all files in html-report
        print('Files in html-report:')
        for root, dirs, files in os.walk('html-report'):
            for file in files:
                print(os.path.join(root, file))
        
        # Copy files directly to the report directory, not to a nested html-report folder
        print(f'Copying html-report/* to {report_dir}/')
        os.system(f'cp -r html-report/* {report_dir}/')
    else:
        print('html-report directory not found, creating a simple index.html')
        with open(f'{report_dir}/index.html', 'w') as f:
            f.write(f'<html><body><h1>Playwright Test Report</h1><p>Run #{run_number}</p></body></html>')
    
    # Load existing reports or create new list
    reports = []
    if os.path.exists('reports.json'):
        try:
            # Make a backup of existing reports.json
            os.system('cp reports.json reports.json.backup')
            print("Created backup of reports.json")
            
            with open('reports.json', 'r') as f:
                content = f.read()
                print(f"Raw content of reports.json: {content}")
                # Only try to parse if content is not empty
                if content.strip():
                    reports = json.loads(content)
                    print(f'Loaded {len(reports)} existing reports from reports.json')
                else:
                    print('reports.json is empty, starting with empty list')
        except json.JSONDecodeError as e:
            print(f'Error decoding reports.json: {str(e)}')
            # Try to recover from potential corrupted files
            if os.path.exists('reports.json.backup'):
                print('Trying to recover from backup')
                try:
                    with open('reports.json.backup', 'r') as f:
                        reports = json.load(f)
                        print(f'Recovered {len(reports)} reports from backup')
                except Exception as e:
                    print(f'Failed to recover from backup: {str(e)}')
            reports = reports or []  # Ensure reports is a list
    else:
        print('reports.json not found, starting with empty list')
        with open('reports.json', 'w') as f:
            json.dump([], f)
            print('Created empty reports.json file')
    
    # Create the report data
    report_data = {
        'sha': commit_sha,
        'message': commit_message,
        'run_number': run_number,
        'run_id': run_id,
        'timestamp': datetime.now().isoformat(),
        'url': f'reports/{commit_sha}/index.html',
        'status': status,
        'duration': duration
    }
    
    # Check if the current commit is already in reports
    existing_index = None
    for i, report in enumerate(reports):
        if report.get('sha') == commit_sha:
            existing_index = i
            break
    
    if existing_index is not None:
        # Update existing report
        print(f'Updating existing report at index {existing_index}')
        reports[existing_index] = report_data
    else:
        # Add new report to the beginning
        print('Adding new report to the beginning')
        reports.insert(0, report_data)
    
    # Keep only last 10 reports
    if len(reports) > 10:
        print(f'Trimming reports from {len(reports)} to 10')
        reports = reports[:10]
    
    # Save updated reports.json
    with open('reports.json', 'w') as f:
        json.dump(reports, f, indent=2)
    print(f'Saved {len(reports)} reports to reports.json')
    
    # Keep only the reports directories mentioned in reports.json
    kept_shas = [report['sha'] for report in reports]
    all_report_dirs = glob.glob('reports/*')
    # Only prune directories if we have reports
    if reports:
        for dir_path in all_report_dirs:
            dir_name = os.path.basename(dir_path)
            if dir_name not in kept_shas and not dir_name.startswith('.'):
                print(f'Removing old report directory: {dir_path}')
                shutil.rmtree(dir_path)
    
    # Generate index.html with links to all reports and status indicators
    template = Template('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Playwright Test Reports</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
            
            /* Visual History Grid Styles */
            .history-grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                grid-template-rows: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 40px;
                max-width: 360px; /* Making grid container smaller */
                margin: 0 auto 40px;
            }
            
            /* Duration Graph Styles */
            .duration-graph {
                margin: 40px auto;
                max-width: 800px;
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .duration-graph h2 {
                margin-top: 0;
                margin-bottom: 20px;
                color: #333;
                font-size: 1.3rem;
            }
            
            .graph-container {
                height: 250px;
                position: relative;
                margin-top: 30px;
                display: flex;
                align-items: flex-end;
                border-bottom: 2px solid #ddd;
                border-left: 2px solid #ddd;
            }
            
            .bar {
                flex: 1;
                background-color: #007bff;
                margin: 0 5px;
                position: relative;
                min-width: 20px;
                transition: height 0.3s ease;
                border-radius: 4px 4px 0 0;
            }
            
            .bar.success {
                background-color: #28a745;
            }
            
            .bar.failure {
                background-color: #dc3545;
            }
            
            .bar-label {
                position: absolute;
                bottom: -25px;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 0.8rem;
                color: #666;
            }
            
            .duration-label {
                position: absolute;
                top: -25px;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 0.8rem;
                color: #666;
            }
            
            .y-axis {
                position: absolute;
                left: -40px;
                top: 0;
                bottom: 0;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                color: #666;
                font-size: 0.8rem;
            }
            
            .y-axis-label {
                margin-right: 10px;
            }
            
            .no-data-message {
                text-align: center;
                color: #666;
                padding: 50px 0;
                font-style: italic;
            }
            
            .history-square {
                aspect-ratio: 1;
                width: 60px; /* Fixed width to make squares smaller */
                height: 60px; /* Fixed height to match width */
                border-radius: 6px; /* Slightly smaller radius to match smaller squares */
                cursor: pointer;
                position: relative;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                color: rgba(255, 255, 255, 0.9);
                font-weight: bold;
                font-size: 0.85rem;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
                text-decoration: none;
            }
            
            .history-square:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10;
            }
            
            .history-square.success {
                background-color: #28a745;
            }
            
            .history-square.failure {
                background-color: #dc3545;
            }
            
            .history-square.unknown {
                background-color: #6c757d;
            }
            
            .history-tooltip {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 4px; /* Reduced padding to fit smaller squares */
                transform: translateY(100%);
                transition: transform 0.2s ease;
                font-size: 0.7em; /* Smaller font size */
                line-height: 1.2; /* Tighter line height */
            }
            
            .history-square:hover .history-tooltip {
                transform: translateY(0);
            }
            
            .history-tooltip .run-number {
                font-weight: bold;
                margin-bottom: 2px; /* Reduced margin for smaller squares */
                font-size: 0.9em; /* Slightly smaller than parent */
            }
            
            .history-tooltip .commit-sha {
                font-family: monospace;
                font-size: 0.8em; /* Smaller than before */
                opacity: 0.8;
                margin-bottom: 1px; /* Add small margin between elements */
            }
            
            .history-tooltip .timestamp {
                font-size: 0.75em; /* Even smaller for dates */
                opacity: 0.7;
            }
            
            .history-tooltip .duration {
                font-size: 0.75em; /* Even smaller for dates */
                opacity: 0.7;
            }
            
            /* Existing styles */
            .report { 
                margin: 20px 0; 
                padding: 20px; 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                position: relative; 
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: transform 0.2s ease;
            }
            .report:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .commit-message { color: #555; margin-bottom: 12px; }
            .timestamp { color: #888; font-size: 0.9em; margin-bottom: 8px; }
            a { color: #0366d6; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .status-indicator {
                display: inline-block;
                width: 14px;
                height: 14px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-success { background-color: #28a745; }
            .status-failure { background-color: #dc3545; }
            .status-unknown { background-color: #6c757d; }
            h1 { 
                margin-bottom: 30px; 
                padding-bottom: 10px; 
                border-bottom: 1px solid #eee; 
                color: #333; 
            }
            h2 { margin-top: 0; }
            .report-count { 
                font-weight: normal; 
                color: #666; 
                margin-left: 10px; 
                font-size: 0.8em;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            footer {
                text-align: center;
                margin-top: 40px;
                color: #888;
                font-size: 0.8em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Playwright Test Reports <span class="report-count">({{ reports|length }} reports)</span></h1>
            
            <!-- Visual History Grid -->
            <div class="history-grid">
                {% for report in reports %}
                <a href="{{ report.url }}" class="history-square {{ report.status }}">
                    {{ report.run_number }}
                    <div class="history-tooltip">
                        <div class="run-number">Run #{{ report.run_number }}</div>
                        <div class="commit-sha">{{ report.sha[:7] }}</div>
                        <div class="timestamp">{{ report.timestamp.split('T')[0] }}</div>
                        {% if report.duration and report.duration != "Unknown" %}
                        <div class="duration">{{ report.duration }}</div>
                        {% endif %}
                    </div>
                </a>
                {% endfor %}
                {% for i in range(10 - reports|length) %}
                <div class="history-square unknown">
                    -
                    <div class="history-tooltip">
                        <div class="run-number">No data</div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Duration Graph -->
            <div class="duration-graph">
                <h2>Build Duration Graph</h2>
                {% if reports|length > 0 %}
                    {% set durations = [] %}
                    {% for report in reports %}
                        {% if report.duration and report.duration != "Unknown" %}
                            {% set seconds = 0 %}
                            {% set parts = report.duration.split(':') %}
                            {% if parts|length == 3 %}
                                {% set seconds = parts[0]|int * 3600 + parts[1]|int * 60 + parts[2]|int %}
                            {% elif parts|length == 2 %}
                                {% set seconds = parts[0]|int * 60 + parts[1]|int %}
                            {% elif parts|length == 1 %}
                                {% set seconds = parts[0]|int %}
                            {% endif %}
                            {% set _ = durations.append(seconds) %}
                        {% else %}
                            {% set _ = durations.append(0) %}
                        {% endif %}
                    {% endfor %}
                    
                    {% set max_duration = namespace(value=1) %}
                    {% if durations|length > 0 %}
                        {% for d in durations %}
                            {% if d > max_duration.value %}
                                {% set max_duration.value = d %}
                            {% endif %}
                        {% endfor %}
                    {% endif %}
                    
                    <div class="graph-container">
                        <div class="y-axis">
                            <div class="y-axis-label">{{ max_duration.value // 60 }}m</div>
                            <div class="y-axis-label">{{ max_duration.value * 3 // 4 // 60 }}m</div>
                            <div class="y-axis-label">{{ max_duration.value // 2 // 60 }}m</div>
                            <div class="y-axis-label">{{ max_duration.value // 4 // 60 }}m</div>
                            <div class="y-axis-label">0m</div>
                        </div>
                        
                        {% for report in reports %}
                            {% set seconds = 0 %}
                            {% if report.duration and report.duration != "Unknown" %}
                                {% set parts = report.duration.split(':') %}
                                {% if parts|length == 3 %}
                                    {% set seconds = parts[0]|int * 3600 + parts[1]|int * 60 + parts[2]|int %}
                                {% elif parts|length == 2 %}
                                    {% set seconds = parts[0]|int * 60 + parts[1]|int %}
                                {% elif parts|length == 1 %}
                                    {% set seconds = parts[0]|int %}
                                {% endif %}
                            {% endif %}
                            
                            {% set height_percent = (seconds / max_duration.value) * 100 if seconds > 0 else 0 %}
                            {% set height = (height_percent * 230 / 100)|round|int %}
                            
                            <div class="bar {{ report.status }}" style="height: {{ height }}px;">
                                <div class="duration-label">{{ report.duration if report.duration and report.duration != "Unknown" else "-" }}</div>
                                <div class="bar-label">Run #{{ report.run_number }}</div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="no-data-message">No duration data available</div>
                {% endif %}
            </div>
            
            <!-- Existing Reports List -->
            {% for report in reports %}
            <div class='report'>
                <h2>
                    <span class='status-indicator status-{% if report.status == "success" %}success{% elif report.status == "failure" %}failure{% else %}unknown{% endif %}'></span>
                    <a href='{{ report.url }}'>Run #{{ report.run_number }}</a>
                </h2>
                <div class='commit-message'>{{ report.message }}</div>
                <div class='timestamp'>{{ report.timestamp.split('T')[0] }} {{ report.timestamp.split('T')[1].split('.')[0] }}</div>
                <div>Commit: {{ report.sha[:7] }}</div>
                {% if report.duration %}
                <div class='duration'>Duration: {{ report.duration }}</div>
                {% endif %}
            </div>
            {% endfor %}
            <footer>
                Generated by GitHub Actions on {{ now }}
            </footer>
        </div>
    </body>
    </html>
    ''')
    
    with open('index.html', 'w') as f:
        f.write(template.render(reports=reports, now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("Generated index.html successfully")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: Script failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
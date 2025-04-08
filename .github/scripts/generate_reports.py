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

def parse_duration_to_seconds(duration_str):
    """Convert a duration string in format HH:MM:SS to seconds."""
    if not duration_str or duration_str == "Unknown":
        return 0
    
    try:
        parts = duration_str.split(':')
        if len(parts) == 3:
            # HH:MM:SS format
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            # MM:SS format
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 1:
            # SS format
            return int(parts[0])
        return 0
    except (ValueError, IndexError):
        print(f"Warning: Could not parse duration string: {duration_str}")
        return 0

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
            # Make a backup of existing reports.json first
            shutil.copy2('reports.json', 'reports.json.backup')
            print("Created backup of reports.json")
            
            with open('reports.json', 'r') as f:
                content = f.read().strip()
                if content:
                    reports = json.loads(content)
                    if not isinstance(reports, list):
                        print('Warning: reports.json does not contain a list, resetting to empty list')
                        reports = []
                    else:
                        print(f'Loaded {len(reports)} existing reports from reports.json')
                else:
                    print('reports.json is empty, starting with empty list')
        except (json.JSONDecodeError, IOError) as e:
            print(f'Error with reports.json: {type(e).__name__}: {str(e)}')
            # Try to recover from backup
            if os.path.exists('reports.json.backup'):
                print('Attempting to recover from backup file')
                try:
                    with open('reports.json.backup', 'r') as f:
                        backup_content = f.read().strip()
                        if backup_content:
                            reports = json.loads(backup_content)
                            if isinstance(reports, list):
                                print(f'Successfully recovered {len(reports)} reports from backup')
                            else:
                                print('Backup does not contain a valid list, using empty list')
                                reports = []
                        else:
                            print('Backup file is empty, using empty list')
                except Exception as recover_err:
                    print(f'Recovery failed: {type(recover_err).__name__}: {str(recover_err)}')
                    reports = []
            else:
                print('No backup file found, using empty list')
                reports = []
    else:
        print('reports.json not found, starting with empty list')
        # Create the file with an empty list
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
            
            .chart-container {
                position: relative;
                height: 300px;
                width: 100%;
                margin-top: 20px;
            }
            
            .no-data-message {
                text-align: center;
                color: #666;
                padding: 50px 0;
                font-style: italic;
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
                    <div class="chart-container">
                        <canvas id="durationChart"></canvas>
                    </div>
                    
                    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
                    <script>
                        // Prepare data for Chart.js
                        const labels = [{% for report in reports|reverse %}'Run #{{ report.run_number }}'{% if not loop.last %}, {% endif %}{% endfor %}];
                        const durations = [
                            {% for report in reports|reverse %}
                                {% set seconds = parse_duration_to_seconds(report.duration) %}
                                {{ seconds // 60 }}{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        ];
                        const statuses = [
                            {% for report in reports|reverse %}
                                '{{ report.status }}'{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        ];
                        const formattedDurations = [
                            {% for report in reports|reverse %}
                                '{{ report.duration if report.duration and report.duration != "Unknown" else "Unknown" }}'{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        ];
                        const commitShas = [
                            {% for report in reports|reverse %}
                                '{{ report.sha[:7] }}'{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        ];
                        
                        // Create point colors based on status
                        const pointBackgroundColors = statuses.map(status => {
                            if (status === 'success') return '#28a745';
                            if (status === 'failure') return '#dc3545';
                            return '#6c757d';
                        });
                        
                        // Create and render the chart
                        document.addEventListener('DOMContentLoaded', function() {
                            const ctx = document.getElementById('durationChart').getContext('2d');
                            const myChart = new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Build Duration (minutes)',
                                        data: durations,
                                        fill: {
                                            target: 'origin',
                                            above: 'rgba(33, 150, 243, 0.1)',
                                        },
                                        borderColor: 'rgba(33, 150, 243, 0.8)',
                                        borderWidth: 3,
                                        tension: 0.2,
                                        pointRadius: 6,
                                        pointHoverRadius: 9,
                                        pointBackgroundColor: pointBackgroundColors,
                                        pointBorderColor: 'rgba(255, 255, 255, 0.8)',
                                        pointBorderWidth: 2
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    interaction: {
                                        mode: 'index',
                                        intersect: false
                                    },
                                    plugins: {
                                        tooltip: {
                                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                            padding: 12,
                                            titleFont: {
                                                size: 14
                                            },
                                            bodyFont: {
                                                size: 13
                                            },
                                            callbacks: {
                                                afterTitle: function(context) {
                                                    const index = context[0].dataIndex;
                                                    return `Commit: ${commitShas[index]}`;
                                                },
                                                label: function(context) {
                                                    const index = context.dataIndex;
                                                    const duration = formattedDurations[index];
                                                    return `Duration: ${duration}`;
                                                }
                                            }
                                        },
                                        legend: {
                                            display: false
                                        }
                                    },
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            title: {
                                                display: true,
                                                text: 'Minutes',
                                                font: {
                                                    weight: 'bold'
                                                }
                                            },
                                            grid: {
                                                color: 'rgba(0, 0, 0, 0.05)'
                                            },
                                            ticks: {
                                                padding: 10
                                            }
                                        },
                                        x: {
                                            grid: {
                                                color: 'rgba(0, 0, 0, 0.05)'
                                            },
                                            ticks: {
                                                padding: 10
                                            }
                                        }
                                    }
                                }
                            });
                        });
                    </script>
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
    
    try:
        rendered_html = template.render(
            reports=reports, 
            now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            parse_duration_to_seconds=parse_duration_to_seconds
        )
        with open('index.html', 'w') as f:
            f.write(rendered_html)
        print("Generated index.html successfully")
    except Exception as e:
        print(f"Error generating index.html: {type(e).__name__}: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: Script failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const modal = document.getElementById('uploadModal');
    const uploadBtn = document.getElementById('uploadBtn');
    const closeBtn = document.querySelector('.close');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const submitUpload = document.getElementById('submitUpload');
    const searchButton = document.getElementById('searchButton');
    const taskInput = document.getElementById('taskInput');
    const thoughtDisplay = document.getElementById('thought-display');
    const performanceSection = document.querySelector('.performance-section');

    // Initialize performance chart
    const ctx = document.getElementById('performanceChart').getContext('2d');
    const performanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Base', 'CoT', 'CoT-Sc', 'Gen. Agent'],
            datasets: [{
                data: [36, 48.2, 46, 0],
                backgroundColor: [
                    'rgba(0, 149, 255, 0.6)',
                    'rgba(0, 149, 255, 0.6)',
                    'rgba(0, 149, 255, 0.6)',
                    'rgba(0, 149, 255, 0.6)'
                ],
                borderColor: [
                    'rgba(0, 149, 255, 0.6)',
                    'rgba(0, 149, 255, 0.6)',
                    'rgba(0, 149, 255, 0.6)',
                    'rgba(0, 149, 255, 0.6)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        color: '#b0b0b0'
                    },
                    grid: {
                        color: 'rgba(64, 64, 64, 0.5)'
                    }
                },
                x: {
                    ticks: {
                        color: '#b0b0b0'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Search functionality
    searchButton.addEventListener('click', () => {
        // Update button state
        searchButton.disabled = true;
        searchButton.textContent = 'Running';
        thoughtDisplay.textContent = 'Running search process... This may take several minutes.';

        // Get task description from input
        const taskDescription = taskInput.value.trim();

        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task: taskDescription
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Get the code display element
                const codeDisplay = document.getElementById('code-display');
                
                // Update the thought display with both the search completion message and the best agent's thought
                thoughtDisplay.innerHTML = data.thoughts.replace(/\n/g, '<br>') + '<br><br>' + 'Best Agent Thought Process:<br>' + data.bestAgent.thought.replace(/\n/g, '<br>');
                
                // Update the code display with the best agent's code
                codeDisplay.textContent = data.bestAgent.code;
                
                // Show the performance section
                performanceSection.classList.add('visible');
                
                // Update the Gen. Agent bar with the best agent's fitness
                performanceChart.data.datasets[0].data[3] = data.bestAgent.fitness.split(": ").slice(-1)[0].replace("%", "");
                performanceChart.update();
                
                // Trigger Prism.js to highlight the new code
                Prism.highlightElement(codeDisplay);
                
                // Reset text color to default
                thoughtDisplay.style.color = '';
            } else {
                let errorMessage = 'Error: ' + data.error;
                if (data.traceback) {
                    errorMessage += '\n\nDetailed error:\n' + data.traceback;
                }
                thoughtDisplay.innerHTML = errorMessage.replace(/\n/g, '<br>');
                thoughtDisplay.style.color = '#ff5252'; // Error color
            }
        })
        .catch(error => {
            console.error('Error:', error);
            thoughtDisplay.innerHTML = 'An error occurred while processing your request:<br>' + error.message;
            thoughtDisplay.style.color = '#ff5252'; // Error color
        })
        .finally(() => {
            // Reset button state
            searchButton.disabled = false;
            searchButton.textContent = 'Search';
            
            // Reset text color after a delay if there was an error
            setTimeout(() => {
                if (thoughtDisplay.style.color === 'rgb(255, 82, 82)') {
                    thoughtDisplay.style.color = '';
                }
            }, 5000);
        });
    });

    // Enter key triggers search
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchButton.click();
        }
    });

    // Modal controls
    uploadBtn.onclick = () => modal.style.display = "block";
    closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (e) => {
        if (e.target == modal) modal.style.display = "none";
    }

    // File drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                fileName.textContent = file.name;
                fileInfo.hidden = false;
            } else {
                alert('Please upload a CSV file');
            }
        }
    }

    submitUpload.addEventListener('click', () => {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modal.style.display = "none";
                updateDatasetInfo(data);
            } else {
                alert('Upload failed: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Upload failed');
        });
    });

    // Add copy button functionality
    const copyButton = document.getElementById('copyCode');
    copyButton.addEventListener('click', () => {
        const code = document.getElementById('code-display').textContent;
        navigator.clipboard.writeText(code).then(() => {
            // Visual feedback
            copyButton.classList.add('copied');
            setTimeout(() => copyButton.classList.remove('copied'), 2000);
        });
    });
});

function updateDatasetInfo(data) {
    const datasetInfo = document.getElementById('datasetInfo');
    const datasetStats = document.getElementById('datasetStats');
    const currentFile = document.getElementById('currentFile');

    datasetInfo.hidden = false;
    currentFile.textContent = `File: ${data.filename}`;

    // Update dataset statistics with just rows and columns
    datasetStats.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${data.rows}</div>
            <div class="stat-label">Rows</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.columns}</div>
            <div class="stat-label">Columns</div>
        </div>
    `;
}

function createPreviewTable(previewData, columns) {
    const table = document.createElement('table');
    table.className = 'preview-table';

    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create body
    const tbody = document.createElement('tbody');
    previewData.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(column => {
            const td = document.createElement('td');
            td.textContent = row[column];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    return table;
}

function generateProcessingCode(columns) {
    return `def process_dataset(data):
    """
    Process the dataset with columns: ${columns.join(', ')}
    """
    results = []
    
    # Process each row
    for row in data:
        # Extract relevant information
        ${columns.map(col => `${col.toLowerCase()} = row['${col}']`).join('\n        ')}
        
        # Your processing logic here
        processed_result = {
            ${columns.map(col => `'${col}': ${col.toLowerCase()}`).join(',\n            ')}
        }
        results.append(processed_result)
    
    return results`;
} 
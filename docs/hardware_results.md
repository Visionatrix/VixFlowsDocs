# Hardware Benchmark Results Graphs

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<script>
fetch('/plotly_data/plotly_data_index.json')
    .then(response => response.json())
    .then(indexData => {
        const suites = Object.keys(indexData);
        const mainContent = document.querySelector('.md-content__inner');

        if (!mainContent) {
            console.error('Main content area not found. Please check the MkDocs template.');
            return;
        }

        // Create a container for all the graphs
        const graphsContainer = document.createElement('div');
        graphsContainer.style.marginTop = '40px';
        mainContent.appendChild(graphsContainer);

        suites.forEach(suite => {
            // Centered Suite Header
            const suiteHeader = document.createElement('h1');
            suiteHeader.textContent = `Test Suite: ${suite}`;
            suiteHeader.style.textAlign = 'center';
            graphsContainer.appendChild(suiteHeader);

            const testCases = indexData[suite];
            testCases.forEach(testCase => {
                const testCaseHeader = document.createElement('h2');

                const containerId = `chart-container-${suite}-${testCase}`;
                const containerDiv = document.createElement('div');
                containerDiv.id = containerId;
                containerDiv.style.marginBottom = '40px';
                graphsContainer.appendChild(containerDiv);

                fetch(`/plotly_data/${suite}_${testCase}.json`)
                    .then(response => {
                        if (!response.ok) throw new Error('Data not found');
                        return response.json();
                    })
                    .then(data => {
                        const traces = [];

                        // Group data by flow_display_name
                        const groupedData = data.reduce((acc, item) => {
                            const key = item.flow_display_name;
                            if (!acc[key]) acc[key] = [];
                            acc[key].push(item);
                            return acc;
                        }, {});

                        // Create a horizontal bar chart for each flow_display_name
                        Object.entries(groupedData).forEach(([flowDisplayName, items]) => {
                            const sortedItems = items.sort((a, b) => b.avg_exec_time - a.avg_exec_time);

                            // Use Unicode line separator for a new line
                            const y = sortedItems.map(item => `${item.hardware_desc}<br>\u2003${item.test_time}\u2003`);
                            const x = sortedItems.map(item => item.avg_exec_time);
                            const hoverText = sortedItems.map(item => `Test Time: ${item.test_time}`);

                            const trace = {
                                y: y,
                                x: x,
                                type: 'bar',
                                orientation: 'h',
                                name: flowDisplayName,
                                text: hoverText,
                                hoverinfo: 'text+x'
                            };

                            traces.push(trace);
                        });

                        const layout = {
                            title: `Average Execution Time (${suite} - ${testCase})`,
                            yaxis: { title: '', automargin: true },
                            xaxis: { title: 'Avg Execution Time (s)' },
                            barmode: 'group',
                            hovermode: 'closest'
                        };

                        Plotly.newPlot(containerId, traces, layout);
                    })
                    .catch(error => console.warn(`No data found for ${suite} - ${testCase}:`, error));
            });
        });
    })
    .catch(error => console.error('Error loading index data:', error));
</script>

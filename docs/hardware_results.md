# Hardware Benchmark Results Graphs

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<script>
fetch('./plotly_data/plotly_data_index.json')
    .then(response => response.json())
    .then(indexData => {
        const suites = Object.keys(indexData);
        const mainContent = document.querySelector('.md-content__inner');

        if (!mainContent) {
            console.error('Main content area not found. Please check the MkDocs template.');
            return;
        }

        const graphsContainer = document.createElement('div');
        graphsContainer.style.marginTop = '40px';
        mainContent.appendChild(graphsContainer);

        suites.forEach(suite => {
            const suiteHeader = document.createElement('h1');
            suiteHeader.textContent = `Test Suite: ${suite}`;
            suiteHeader.style.textAlign = 'center';
            graphsContainer.appendChild(suiteHeader);

            const testCases = indexData[suite];
            testCases.forEach(testCase => {
                const containerId = `chart-container-${suite}-${testCase}`;
                const containerDiv = document.createElement('div');
                containerDiv.id = containerId;
                containerDiv.style.marginBottom = '40px';

                // Checkbox for toggling disable_smart_memory results
                const toggleCheckbox = document.createElement('input');
                toggleCheckbox.type = 'checkbox';
                toggleCheckbox.id = `toggle-smart-memory-${suite}-${testCase}`;
                toggleCheckbox.style.margin = '10px';
                const toggleLabel = document.createElement('label');
                toggleLabel.textContent = 'Show Disable Smart Memory Results';
                toggleLabel.htmlFor = toggleCheckbox.id;

                // Attach them to the DOM now, but we may remove them later if unnecessary
                graphsContainer.appendChild(toggleLabel);
                graphsContainer.appendChild(toggleCheckbox);
                graphsContainer.appendChild(containerDiv);

                // Load data and create the chart
                fetch(`./plotly_data/${suite}_${testCase}.json`)
                    .then(response => {
                        if (!response.ok) throw new Error('Data not found');
                        return response.json();
                    })
                    .then(data => {
                        // Determine if we have any results with disable_smart_memory === true
                        const hasSmartMemoryTrue = data.some(item => item.disable_smart_memory === true);

                        // If none of the items have disable_smart_memory === true, remove the checkbox and label
                        if (!hasSmartMemoryTrue) {
                            toggleCheckbox.remove();
                            toggleLabel.remove();
                        }

                        const groupedData = data.reduce((acc, item) => {
                            const key = item.flow_display_name;
                            if (!acc[key]) acc[key] = [];
                            acc[key].push(item);
                            return acc;
                        }, {});

                        function updateChart() {
                            const showDisableSmartMemory = toggleCheckbox.checked;
                            const filteredTraces = [];

                            // Build traces from items
                            Object.entries(groupedData).forEach(([flowDisplayName, items]) => {
                                const filteredItems = items.filter(item =>
                                    showDisableSmartMemory
                                        ? item.disable_smart_memory === true
                                        : item.disable_smart_memory !== true
                                );

                                if (filteredItems.length > 0) {
                                    // Sort from highest to lowest for a nicer stacked/horizontal look
                                    const sortedItems = filteredItems.sort((a, b) => b.avg_exec_time - a.avg_exec_time);
                                    const y = sortedItems.map(item => `${item.hardware_desc}<br>\u2003${item.test_time}\u2003`);
                                    const x = sortedItems.map(item => item.avg_exec_time);
                                    const hoverText = sortedItems.map(item => `Test Time: ${item.test_time}`);

                                    filteredTraces.push({
                                        y,
                                        x,
                                        type: 'bar',
                                        orientation: 'h',
                                        name: flowDisplayName,
                                        text: hoverText,
                                        hoverinfo: 'text+x',
                                        showlegend: true
                                    });
                                }
                            });

                            const layout = {
                                title: `${suite} - ${testCase}`,
                                yaxis: { title: '', automargin: true },
                                xaxis: { title: 'Avg Execution Time (s)' },
                                barmode: 'group',
                                hovermode: 'closest',
                                showlegend: true
                            };

                            Plotly.react(containerId, filteredTraces, layout);
                        }

                        // Initial draw
                        updateChart();

                        // Re-draw the chart upon toggling, if the checkbox is present
                        toggleCheckbox.addEventListener('change', updateChart);
                    })
                    .catch(error => {
                        console.warn(`No data found for ${suite} - ${testCase}:`, error);
                        // If there's no data at all, remove the whole container & toggles
                        containerDiv.remove();
                        toggleCheckbox.remove();
                        toggleLabel.remove();
                    });
            });
        });
    })
    .catch(error => console.error('Error loading index data:', error));
</script>

document.addEventListener('DOMContentLoaded', function() {
    const symbolSelect = document.getElementById('symbol-select');
    const timeframeSelect = document.getElementById('timeframe-select');
    const chartContainer = document.getElementById('chart-container');
    let chart = null;
    let candleSeries = null;
    let volumeSeries = null;

    function clearChart() {
        if (chart) {
            chart.remove();
            chart = null;
            candleSeries = null;
            volumeSeries = null;
        }
        const old = document.getElementById('lightweight-chart');
        if (old) old.remove();
    }

    function updateChart() {
        const selectedSymbol = symbolSelect.value;
        const selectedTimeframe = timeframeSelect.value;

        clearChart();

        if (selectedSymbol && selectedTimeframe) {
            chartContainer.querySelector('.placeholder')?.remove();
            const toolbar = chartContainer.querySelector('.chart-toolbar');
            if (toolbar) toolbar.style.display = 'flex';
            const chartDiv = document.createElement('div');
            chartDiv.id = 'lightweight-chart';
            chartContainer.appendChild(chartDiv);
            chartDiv.innerHTML = `<div class=\"spinner\"></div>`;

            fetch(`/api/get_chart/${selectedSymbol}/${selectedTimeframe}`)
                .then(response => response.json())
                .then(data => {
                    chartDiv.innerHTML = '';
                    if (data.error) {
                        chartDiv.innerHTML = `<div class=\"placeholder\"><p>${data.error}</p></div>`;
                        return;
                    }
                    chart = LightweightCharts.createChart(chartDiv, {
                        layout: {
                            background: { color: getComputedStyle(document.documentElement).getPropertyValue('--bg-light').trim() },
                            textColor: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(),
                            fontFamily: 'Inter, sans-serif',
                        },
                        grid: {
                            vertLines: { color: '#23273a', style: 0, visible: true },
                            horzLines: { color: '#23273a', style: 0, visible: true },
                        },
                        width: chartDiv.offsetWidth,
                        height: chartDiv.offsetHeight || 350,
                        timeScale: {
                            borderColor: '#2A2E39',
                            timeVisible: true,
                            secondsVisible: false,
                        },
                        rightPriceScale: {
                            borderColor: '#2A2E39',
                        },
                        crosshair: {
                            mode: LightweightCharts.CrosshairMode.Normal,
                        },
                    });
                    candleSeries = chart.addCandlestickSeries({
                        upColor: '#26a69a',
                        downColor: '#ef5350',
                        borderUpColor: '#26a69a',
                        borderDownColor: '#ef5350',
                        wickUpColor: '#26a69a',
                        wickDownColor: '#ef5350',
                        priceLineVisible: false,
                    });
                    candleSeries.setData(data.ohlcv.map(bar => ({
                        time: bar.time,
                        open: bar.open,
                        high: bar.high,
                        low: bar.low,
                        close: bar.close
                    })));
                    // Responsive resize
                    window.addEventListener('resize', () => {
                        if (chartDiv && chart) {
                            chart.applyOptions({ width: chartDiv.offsetWidth, height: chartDiv.offsetHeight || 350 });
                        }
                    });
                })
                .catch(error => {
                    console.error("Fetch Error:", error);
                    chartDiv.innerHTML = `<div class=\"placeholder\"><p>A critical error occurred. Check terminal for details.</p></div>`;
                });
        }
    }
    

    fetch('/api/get_symbols')
        .then(res => res.json())
        .then(symbols => {
            symbolSelect.innerHTML = '<option value="">-- Choose Symbol --</option>';
            symbols.forEach(s => {
                const option = document.createElement('option');
                option.value = s;
                option.textContent = s;
                symbolSelect.appendChild(option);
            });
            // Initialize Choices.js for search functionality and consistent style
            if (window.Choices) {
                new Choices(symbolSelect, {
                    searchEnabled: true,
                    itemSelectText: '',
                    shouldSort: false,
                    searchChoices: true,
                    classNames: {
                        containerOuter: 'choices symbol-choices',
                        input: 'choices__input symbol-choices-input',
                        listDropdown: 'choices__list--dropdown symbol-choices-dropdown',
                    },
                    renderChoiceLimit: -1,
                    searchResultLimit: 100,
                    removeItemButton: false,
                    placeholder: true,
                    placeholderValue: '-- Choose Symbol --',
                });
            }
        });

    symbolSelect.addEventListener('change', updateChart);
    timeframeSelect.addEventListener('change', updateChart);
});
document.addEventListener('DOMContentLoaded', function() {
    // Les éléments dyal l'HTML
    const symbolSelect = document.getElementById('symbol-select');
    const timeframeSelect = document.getElementById('timeframe-select');
    const chartContainer = document.getElementById('chart-container');

    // Variables dyal l'chart
    let chart = null;
    let candleSeries = null;
    let lastCandle = null; // Kan7tafdo b akher chem3a
    
    // Timers
    let countdownInterval = null;
    let tickInterval = null; 

    function getTimeframeInSeconds(timeframe) {
        const unit = timeframe.slice(-1);
        const value = parseInt(timeframe.slice(0, -1));
        if (unit === 'M') return value * 60;
        if (unit === 'H') return value * 3600;
        if (unit === 'D') return value * 86400;
        return 0;
    }

    function clearChart() {
        if (countdownInterval) clearInterval(countdownInterval);
        if (tickInterval) clearInterval(tickInterval);
        countdownInterval = null;
        tickInterval = null;
        lastCandle = null;

        const countdownContainer = document.getElementById('countdown-container');
        if (countdownContainer) countdownContainer.style.display = 'none';

        if (chart) {
            chart.remove();
            chart = null;
            candleSeries = null;
        }
        const old = document.getElementById('lightweight-chart');
        if (old) old.remove();
    }

    // Function jdida katjib live price w kat'actualisi l'chart
    function startLiveUpdate(symbol) {
        if (tickInterval) clearInterval(tickInterval);

        tickInterval = setInterval(() => {
            fetch(`/api/get_ticks/${symbol}`)
                .then(response => {
                    if (!response.ok) return null; // Ila kan error f server, nskto
                    return response.json();
                })
                .then(tickData => {
                    // Kanchofo wach kayna data jdida w wach l'chart ba9i
                    if (tickData && tickData.price && candleSeries && lastCandle) {
                        
                        // ***** START OF THE FIX *****
                        // Hada howa l'7el bach l'chart it7errek b7al TradingView
                        
                        // 1. Kan'7esbo l'high w low jdad dyal l'chem3a
                        lastCandle.high = Math.max(lastCandle.high, tickData.price);
                        lastCandle.low = Math.min(lastCandle.low, tickData.price);
                        
                        // 2. Kan'beddlo l'prix dyal l'ighla9 (close)
                        lastCandle.close = tickData.price;
                        
                        // 3. Kan'sifto l'candle l'mbeddla l'chart bach t'actualisa
                        candleSeries.update(lastCandle);
                        // ***** END OF THE FIX *****
                    }
                })
                .catch(error => { /* Nskto 3la les erreurs dyal ticks */ });
        }, 1200); // Kol 1.2 tania
    }

    function updateChart() {
        const selectedSymbol = symbolSelect.value;
        const selectedTimeframe = timeframeSelect.value;

        clearChart();

        if (selectedSymbol && selectedTimeframe) {
            chartContainer.querySelector('.placeholder')?.remove();
            const chartDiv = document.createElement('div');
            chartDiv.id = 'lightweight-chart';
            chartContainer.appendChild(chartDiv);
            chartDiv.innerHTML = `<div class="spinner-wrapper"><div class="spinner"></div></div>`;

            fetch(`/api/get_chart/${selectedSymbol}/${selectedTimeframe}`)
                .then(response => response.json())
                .then(data => {
                    chartDiv.innerHTML = '';
                    if (data.error || !data.ohlcv || data.ohlcv.length === 0) {
                        chartDiv.innerHTML = `<div class="placeholder"><p>${data.error || "No chart data."}</p></div>`;
                        return;
                    }
                    
                    chart = LightweightCharts.createChart(chartDiv, {
                        layout: { background: { color: 'transparent' }, textColor: '#D1D4DC', fontFamily: 'Inter, sans-serif' },
                        grid: { vertLines: { color: '#23273a' }, horzLines: { color: '#23273a' } },
                        width: chartDiv.offsetWidth, height: chartDiv.offsetHeight,
                        timeScale: { borderColor: '#2A2E39', timeVisible: true, secondsVisible: false },
                        rightPriceScale: { borderColor: '#2A2E39' },
                        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
                    });

                    candleSeries = chart.addCandlestickSeries({
                        upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
                        wickUpColor: '#26a69a', wickDownColor: '#ef5350',
                    });
                    
                    candleSeries.setData(data.ohlcv);
                    lastCandle = data.ohlcv[data.ohlcv.length - 1];
                    
                    // Kheddem l'countdown dyal l'chem3a
                    const timeframeInSeconds = getTimeframeInSeconds(selectedTimeframe);
                    const countdownContainer = document.getElementById('countdown-container');
                    const countdownEl = document.getElementById('candle-countdown');
                    
                    // ** L'7el dyal l'Countdown **
                    if (timeframeInSeconds > 0 && countdownContainer && countdownEl) {
                        const candleCloseTime = (lastCandle.time + timeframeInSeconds) * 1000;
                        
                        const updateCountdown = () => {
                            const remaining = candleCloseTime - new Date().getTime();
                            if (remaining <= 0) {
                                countdownEl.textContent = "00:00";
                                clearInterval(countdownInterval);
                                setTimeout(updateChart, 1500); // N3awdo njibo chart jdid
                                return;
                            }
                            const minutes = Math.floor((remaining / 1000) / 60);
                            const seconds = Math.floor((remaining / 1000) % 60);
                            countdownEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                        };
                        updateCountdown();
                        countdownInterval = setInterval(updateCountdown, 1000);
                        countdownContainer.style.display = 'flex'; // Kanbeyyno l'countdown
                    }

                    // Kheddem l'live update dyal l'prix
                    startLiveUpdate(selectedSymbol);

                    new ResizeObserver(() => chart.timeScale().fitContent()).observe(chartDiv);
                    chart.timeScale().fitContent();

                })
                .catch(error => {
                    console.error("Chart Fetch Error:", error);
                    chartDiv.innerHTML = `<div class="placeholder"><p>Error loading chart.</p></div>`;
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
            if (window.Choices) { new Choices(symbolSelect, { searchEnabled: true, itemSelectText: '' }); }
        });

    symbolSelect.addEventListener('change', updateChart);
    timeframeSelect.addEventListener('change', updateChart);
});
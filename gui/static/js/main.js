// gui/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration des éléments du DOM ---
    const chartContainer = document.getElementById('chart-container');
    const logConsole = document.getElementById('log-console');
    const signalList = document.getElementById('signal-list');
    const statusIndicator = document.getElementById('status-indicator');

    // --- Initialisation du Chart avec le thème DARK ---
    const chart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
            backgroundColor: '#131722', // Couleur de fond principale
            textColor: '#d1d4dc',       // Couleur du texte
        },
        grid: {
            vertLines: { color: '#2a2e39' }, // Lignes verticales de la grille
            horzLines: { color: '#2a2e39' }, // Lignes horizontales de la grille
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#485158', // Bordure de l'échelle des prix
        },
        timeScale: {
            borderColor: '#485158', // Bordure de l'échelle de temps
            timeVisible: true,
            secondsVisible: false,
        },
    });

    const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',      // Couleur des bougies haussières
        downColor: '#ef5350',    // Couleur des bougies baissières
        borderDownColor: '#ef5350',
        borderUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        wickUpColor: '#26a69a',
    });
    
    // Gérer le redimensionnement du chart pour qu'il reste responsive
    new ResizeObserver(entries => {
        if (entries.length === 0 || entries[0].target !== chartContainer) { return; }
        const newRect = entries[0].contentRect;
        chart.applyOptions({ width: newRect.width, height: newRect.height });
    }).observe(chartContainer);

    // --- Logique des Tabs ---
    window.openTab = (evt, tabName) => {
        let i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
            tabcontent[i].classList.remove("active");
        }
        tablinks = document.getElementsByClassName("tab-link");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(tabName).style.display = "flex";
        document.getElementById(tabName).classList.add("active");
        evt.currentTarget.className += " active";
    };
    // Activer le premier tab par défaut au démarrage
    document.querySelector('.tab-link').click();

    // === FONCTIONS GLOBALES APPELÉES PAR PYTHON ===
    
    window.addLogMessage = (message, level = 'info') => {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-message ${level}`;
        logEntry.innerHTML = `<span class="timestamp">${timestamp}</span> <span class="message">${message}</span>`;
        logConsole.appendChild(logEntry);
        logConsole.scrollTop = logConsole.scrollHeight;
    };

    window.addTradeSignal = (data) => {
        addTradeSignalCard(data);
        drawTradeOnChart(data);
    };

    window.updateChart = (data) => {
        candlestickSeries.update(data);
    };

    window.loadHistoricalData = (data) => {
        if (data && data.length > 0) {
            console.log(`Loading ${data.length} historical bars...`);
            candlestickSeries.setData(data);
            chart.timeScale().fitContent();
        } else {
            console.log("Received empty historical data.");
        }
    };

    // --- Fonctions d'aide pour l'affichage ---

    function addTradeSignalCard(data) {
        const card = document.createElement('div');
        const signalClass = data.signal.toLowerCase();
        card.className = `signal-card ${signalClass}`;
        card.innerHTML = `
            <div class="signal-card-header">
                <span class="symbol">${data.symbol}</span>
                <span class="signal-type ${signalClass}">${data.signal}</span>
            </div>
            <div class="signal-card-body">
                <div><span class="label">Entry Price</span><span>${data.entry_price}</span></div>
                <div><span class="label">Risk/Reward</span><span>1 : ${data.risk_reward}</span></div>
                <div><span class="label">Stop Loss</span><span>${data.stop_loss} (${data.sl_pips} pips)</span></div>
                <div><span class="label">Take Profit</span><span>${data.take_profit} (${data.tp_pips} pips)</span></div>
            </div>`;
        signalList.prepend(card);
    }

    function drawTradeOnChart(trade) {
        const slLine = { price: trade.stop_loss, color: '#ef5350', lineWidth: 2, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: 'SL' };
        const tpLine = { price: trade.take_profit, color: '#26a69a', lineWidth: 2, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: 'TP' };
        candlestickSeries.createPriceLine(slLine);
        candlestickSeries.createPriceLine(tpLine);
        candlestickSeries.setMarkers([
            ...candlestickSeries.markers(),
            {
                time: (new Date(trade.breakout_candle_time).getTime() / 1000),
                position: trade.signal === 'BUY' ? 'belowBar' : 'aboveBar',
                color: '#2962ff',
                shape: trade.signal === 'BUY' ? 'arrowUp' : 'arrowDown',
                text: `${trade.signal} @ ${trade.entry_price}`
            }
        ]);
    }

    statusIndicator.className = 'status-connected';
    addLogMessage('Desktop application UI loaded. Waiting for bot connection...', 'info');
});
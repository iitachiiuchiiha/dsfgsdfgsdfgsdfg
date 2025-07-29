const app = {
    chart: null,
    candlestickSeries: null,
    elements: {},
    availableSymbols: [],

    init: function() {
        this.cacheElements();
        this.setupEventListeners();
        this.addLogMessage('Interface prête. Demande de la liste des symboles...', 'info');
        this.fetchSymbols();
    },

    cacheElements: function() {
        this.elements = {
            chartContainer: document.getElementById('chart-container'),
            logConsole: document.getElementById('log-console'),
            symbolInput: document.getElementById('symbol-input'),
            loadChartBtn: document.getElementById('load-chart-btn'),
            symbolResults: document.getElementById('symbol-results'),
            timeframeSelect: document.getElementById('timeframe-select'),
            chartPlaceholder: document.getElementById('chart-placeholder'),
            statusIndicator: document.getElementById('status-indicator'),
        };
    },

    setupEventListeners: function() {
        this.elements.loadChartBtn.addEventListener('click', () => this.handleLoadChart());
        this.elements.symbolInput.addEventListener('input', (e) => this.filterAndShowSymbols(e.target.value));
        document.addEventListener('click', (e) => {
            if (!this.elements.symbolResults.contains(e.target)) {
                this.elements.symbolResults.style.display = 'none';
            }
        });
    },

    setupChart: function() {
        if (this.chart) return;
        if (!this.elements.chartContainer) return;
        
        if(this.elements.chartPlaceholder) this.elements.chartPlaceholder.style.display = 'none';

        this.chart = LightweightCharts.createChart(this.elements.chartContainer, {
            width: this.elements.chartContainer.clientWidth,
            height: this.elements.chartContainer.clientHeight,
            layout: { backgroundColor: '#131722', textColor: '#d1d4dc' },
            grid: { vertLines: { color: '#2a2e39' }, horzLines: { color: '#2a2e39' } },
            crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
            rightPriceScale: { borderColor: '#485158' },
            timeScale: { borderColor: '#485158', timeVisible: true, secondsVisible: false },
        });

        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#26a69a', downColor: '#ef5350',
            borderDownColor: '#ef5350', borderUpColor: '#26a69a',
            wickDownColor: '#ef5350', wickUpColor: '#26a69a',
        });
        
        new ResizeObserver(entries => {
            if (!entries || entries.length === 0) return;
            const { width, height } = entries[0].contentRect;
            this.chart.applyOptions({ width, height });
        }).observe(this.elements.chartContainer);
    },

    fetchSymbols: async function() {
        try {
            const response = await fetch('/api/symbols');
            if (!response.ok) throw new Error(`Erreur serveur: ${response.status}`);
            const symbols = await response.json();
            this.availableSymbols = symbols;
            this.addLogMessage(`${symbols.length} symboles reçus de MT5.`, 'info');
            this.elements.statusIndicator.className = 'status-connected';
        } catch (e) {
            this.addLogMessage("Erreur: Impossible de charger la liste des symboles.", 'error');
            this.elements.statusIndicator.className = 'status-disconnected';
        }
    },

    handleLoadChart: async function() {
        const symbol = this.elements.symbolInput.value.trim().toUpperCase();
        const timeframe = this.elements.timeframeSelect.value;
        if (!symbol) {
            this.addLogMessage("Veuillez entrer un symbole.", 'warning');
            return;
        }

        this.addLogMessage(`Demande de chargement: ${symbol} (${timeframe})...`, 'info');
        this.setupChart();

        try {
            const response = await fetch(`/api/historical_data?symbol=${symbol}&timeframe=${timeframe}`);
            if (!response.ok) throw new Error(`Erreur serveur: ${response.status}`);
            const historicalData = await response.json();
            this.loadHistoricalData(historicalData);
        } catch (e) {
            this.addLogMessage(`Erreur lors du chargement du chart pour ${symbol}.`, 'error');
        }
    },
    
    filterAndShowSymbols: function(query) {
        this.elements.symbolResults.innerHTML = '';
        if (!query) {
            this.elements.symbolResults.style.display = 'none';
            return;
        }
        const filtered = this.availableSymbols.filter(s => s.toLowerCase().includes(query.toLowerCase())).slice(0, 10);
        if (filtered.length > 0) {
            filtered.forEach(symbol => {
                const item = document.createElement('div');
                item.textContent = symbol;
                item.addEventListener('click', () => {
                    this.elements.symbolInput.value = symbol;
                    this.elements.symbolResults.style.display = 'none';
                });
                this.elements.symbolResults.appendChild(item);
            });
            this.elements.symbolResults.style.display = 'block';
        } else {
            this.elements.symbolResults.style.display = 'none';
        }
    },

    loadHistoricalData: function(data) {
        if (this.candlestickSeries && data && data.length > 0) {
            this.candlestickSeries.setData(data);
            this.chart.timeScale().fitContent();
        } else {
            this.addLogMessage("Aucune donnée historique reçue pour ce symbole.", 'error');
        }
    },
    
    addLogMessage: function(message, level = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-message ${level}`;
        logEntry.innerHTML = `<span class="timestamp">${timestamp}</span> <span class="message">${message}</span>`;
        this.elements.logConsole.appendChild(logEntry);
        this.elements.logConsole.scrollTop = this.elements.logConsole.scrollHeight;
    },

    openTab: function(evt, tabName) {
        let i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].classList.remove("active");
        }
        tablinks = document.getElementsByClassName("tab-link");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].classList.remove("active");
        }
        document.getElementById(tabName).classList.add("active");
        evt.currentTarget.classList.add("active");
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
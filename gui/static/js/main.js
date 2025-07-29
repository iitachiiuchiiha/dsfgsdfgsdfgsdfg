// gui/static/js/main.js

/**
 * On encapsule toute la logique dans un objet 'app' pour une meilleure organisation
 * et pour éviter les variables globales qui peuvent causer des conflits.
 */
const app = {
    chart: null,
    candlestickSeries: null,
    elements: {},

    /**
     * Point d'entrée principal. Cette fonction est appelée une fois que le DOM est prêt.
     */
    init: function() {
        console.log("DOM est prêt. Initialisation de l'application...");
        this.cacheElements();
        this.setupChart();
        this.setupTabs();
        this.setupApiBridge();

        this.elements.statusIndicator.className = 'status-connected';
        this.addLogMessage('Interface utilisateur initialisée. En attente de la connexion du bot...', 'info');
    },

    /**
     * Met en cache les éléments du DOM pour un accès plus rapide et plus propre.
     */
    cacheElements: function() {
        this.elements.chartContainer = document.getElementById('chart-container');
        this.elements.logConsole = document.getElementById('log-console');
        this.elements.signalList = document.getElementById('signal-list');
        this.elements.statusIndicator = document.getElementById('status-indicator');
    },

    /**
     * Configure et initialise le Lightweight Chart.
     */
    setupChart: function() {
        if (!this.elements.chartContainer) {
            console.error("ERREUR CRITIQUE: Le conteneur du chart #chart-container est introuvable.");
            return;
        }

        // On vérifie que la librairie est bien chargée avant de l'utiliser
        if (typeof LightweightCharts === 'undefined' || typeof LightweightCharts.createChart !== 'function') {
            console.error("ERREUR CRITIQUE: La librairie LightweightCharts n'est pas chargée correctement.");
            this.addLogMessage("Erreur: La librairie du chart n'a pas pu être chargée.", 'error');
            return;
        }

        console.log("Création du chart...");
        this.chart = LightweightCharts.createChart(this.elements.chartContainer, {
            width: this.elements.chartContainer.clientWidth,
            height: this.elements.chartContainer.clientHeight,
            layout: { backgroundColor: '#131722', textColor: '#d1d4dc' },
            grid: { vertLines: { color: '#2a2e39' }, horzLines: { color: '#2a2e39' } },
            crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
            rightPriceScale: { borderColor: '#485158' },
            timeScale: { borderColor: '#485158', timeVisible: true, secondsVisible: false },
        });

        console.log("Chart créé. Ajout de la série de bougies...");
        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#26a69a', downColor: '#ef5350',
            borderDownColor: '#ef5350', borderUpColor: '#26a69a',
            wickDownColor: '#ef5350', wickUpColor: '#26a69a',
        });
        console.log("Série de bougies ajoutée avec succès.");

        // Gérer le redimensionnement pour que le chart reste responsive
        new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== this.elements.chartContainer) { return; }
            const newRect = entries[0].contentRect;
            this.chart.applyOptions({ width: newRect.width, height: newRect.height });
        }).observe(this.elements.chartContainer);
    },

    /**
     * Configure la logique des onglets (tabs).
     */
    setupTabs: function() {
        window.openTab = (evt, tabName) => {
            let i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) tabcontent[i].style.display = "none";
            tablinks = document.getElementsByClassName("tab-link");
            for (i = 0; i < tablinks.length; i++) tablinks[i].className = tablinks[i].className.replace(" active", "");
            document.getElementById(tabName).style.display = "flex";
            evt.currentTarget.className += " active";
        };
        document.querySelector('.tab-link').click();
    },

    /**
     * Met en place les fonctions globales qui seront appelées par Python (le "pont").
     */
    setupApiBridge: function() {
        window.addLogMessage = this.addLogMessage.bind(this);
        window.addTradeSignal = (data) => {
            this.addTradeSignalCard(data);
            this.drawTradeOnChart(data);
        };
        window.updateChart = this.updateChart.bind(this);
        window.loadHistoricalData = this.loadHistoricalData.bind(this);
    },

    // --- Fonctions de l'API appelées par Python ---

    addLogMessage: function(message, level = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-message ${level}`;
        logEntry.innerHTML = `<span class="timestamp">${timestamp}</span> <span class="message">${message}</span>`;
        this.elements.logConsole.appendChild(logEntry);
        this.elements.logConsole.scrollTop = this.elements.logConsole.scrollHeight;
    },

    updateChart: function(data) {
        if (this.candlestickSeries) {
            this.candlestickSeries.update(data);
        }
    },

    loadHistoricalData: function(data) {
        if (this.candlestickSeries && data && data.length > 0) {
            console.log(`Chargement de ${data.length} bougies historiques...`);
            this.candlestickSeries.setData(data);
            this.chart.timeScale().fitContent();
            console.log("Données historiques chargées.");
        } else {
            console.error("Échec du chargement des données historiques: données vides ou série non prête.");
        }
    },

    // --- Fonctions d'aide pour l'affichage ---

    addTradeSignalCard: function(data) {
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
        this.elements.signalList.prepend(card);
    },

    drawTradeOnChart: function(trade) {
        const slLine = { price: trade.stop_loss, color: '#ef5350', lineWidth: 2, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: 'SL' };
        const tpLine = { price: trade.take_profit, color: '#26a69a', lineWidth: 2, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: 'TP' };
        this.candlestickSeries.createPriceLine(slLine);
        this.candlestickSeries.createPriceLine(tpLine);
        this.candlestickSeries.setMarkers([
            ...this.candlestickSeries.markers(),
            {
                time: (new Date(trade.breakout_candle_time).getTime() / 1000),
                position: trade.signal === 'BUY' ? 'belowBar' : 'aboveBar',
                color: '#2962ff',
                shape: trade.signal === 'BUY' ? 'arrowUp' : 'arrowDown',
                text: `${trade.signal} @ ${trade.entry_price}`
            }
        ]);
    }
};

// --- Point d'entrée du script ---
// On attend que le DOM soit complètement chargé avant de lancer notre application.
document.addEventListener('DOMContentLoaded', () => app.init());

// ============================================
// SIMPLE MOVING AVERAGE CROSSOVER STRATEGY
// Run: node strategy.js
// ============================================

// ---------- 1. INDICATORS ----------
function SMA(prices, period) {
    return prices.map((_, i) => {
        if (i < period - 1) return null;
        const slice = prices.slice(i - period + 1, i + 1);
        return slice.reduce((a, b) => a + b, 0) / period;
    });
}

// ---------- 2. GENERATE FAKE PRICE DATA ----------
function generatePrices(n = 300, start = 100) {
    const prices = [start];
    for (let i = 1; i < n; i++) {
        const change = (Math.random() - 0.48) * 2; // slight upward drift
        prices.push(Math.max(1, prices[i - 1] + change));
    }
    return prices;
}

// ---------- 3. BACKTEST ----------
function backtest(prices, fastPeriod = 10, slowPeriod = 30, capital = 10000) {
    const fast = SMA(prices, fastPeriod);
    const slow = SMA(prices, slowPeriod);

    let cash = capital;
    let shares = 0;
    let trades = [];

    for (let i = 1; i < prices.length; i++) {
        if (fast[i] == null || slow[i] == null) continue;

        const buySignal  = fast[i - 1] <= slow[i - 1] && fast[i] > slow[i];
        const sellSignal = fast[i - 1] >= slow[i - 1] && fast[i] < slow[i];
        const price = prices[i];

        if (buySignal && shares === 0) {
            shares = Math.floor(cash / price);
            cash -= shares * price;
            trades.push({ day: i, type: 'BUY', price: price.toFixed(2), shares });
        } 
        else if (sellSignal && shares > 0) {
            cash += shares * price;
            trades.push({ day: i, type: 'SELL', price: price.toFixed(2), shares });
            shares = 0;
        }
    }

    // Liquidate at end
    const finalValue = cash + shares * prices[prices.length - 1];
    const buyHoldValue = (capital / prices[0]) * prices[prices.length - 1];

    return {
        initialCapital: capital,
        finalValue: finalValue.toFixed(2),
        strategyReturn: (((finalValue - capital) / capital) * 100).toFixed(2) + '%',
        buyHoldReturn: (((buyHoldValue - capital) / capital) * 100).toFixed(2) + '%',
        totalTrades: trades.length,
        trades
    };
}

// ---------- 4. RUN ----------
const prices = generatePrices(300, 100);
const result = backtest(prices, 10, 30, 10000);

console.log('\n📈 SIMPLE SMA CROSSOVER BACKTEST\n');
console.log('Starting capital : $' + result.initialCapital);
console.log('Final value      : $' + result.finalValue);
console.log('Strategy return  : ' + result.strategyReturn);
console.log('Buy & hold return: ' + result.buyHoldReturn);
console.log('Total trades     : ' + result.totalTrades);

console.log('\n📋 Trade Log:');
console.table(result.trades.slice(0, 10)); // first 10 trades
if (result.trades.length > 10) {
    console.log(`... and ${result.trades.length - 10} more trades`);
}
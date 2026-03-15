# Quantitative Multi-Factor Equity Strategy – Brazilian Equities (B3)

## Project Overview

This repository implements a systematic quantitative investment strategy for the Brazilian stock market (B3). The project encompasses the complete research pipeline from raw market data acquisition to factor-based portfolio construction and historical backtesting. The objective is to evaluate whether a multi-factor ranking model incorporating momentum, liquidity, and volatility characteristics can generate risk-adjusted excess returns relative to the IBOVESPA benchmark.

The analysis is supported by a Power BI dashboard for performance visualization and portfolio monitoring.

---

## Research Framework

The project tests a cross-sectional factor model applied to Brazilian equities, where assets are ranked according to a composite score derived from multiple quantitative signals. The underlying hypothesis posits that stocks exhibiting favorable combinations of momentum, liquidity, and return stability may outperform the broader market over time, and that a systematic rules-based approach can capture this premium.

The methodology follows a structured quantitative workflow:

1. Market data acquisition and storage
2. Factor computation for each asset
3. Cross-sectional ranking and scoring
4. Portfolio construction based on ranked signals
5. Historical backtesting with transaction costs
6. Performance analysis and benchmarking

---

## Data Infrastructure

### Data Source
Market data is retrieved via the Yahoo Finance API using the yfinance library. The dataset includes daily observations for major IBOVESPA constituents and liquid B3 equities.

### Data Schema
For each asset, the following fields are stored in a SQLite database:

- Ticker identifier
- Trading date
- Open, high, low, close prices
- Trading volume
- Timestamp of data ingestion

### Database Structure
The database layer implements:

- Automated table creation for price history
- Duplicate handling via UNIQUE constraints on (ticker, date)
- Excel export functionality for external analysis
- Parameterized queries for efficient data retrieval

---

## Factor Model Specification

The strategy employs three independent factors representing distinct dimensions of equity returns. Each factor is calculated using rolling windows to ensure forward-looking consistency in backtesting.

### Momentum Factor
Economic rationale: Assets with positive price persistence tend to continue their trajectory in the short-to-medium term.

Calculation:
- 12-month cumulative return
- Normalization: Cross-sectional percentile ranking

### Liquidity Factor
Economic rationale: Highly traded stocks offer lower transaction costs and reduced price impact, enabling efficient portfolio implementation.

Calculation:
- Average daily traded volume (21-day window)
- Amihud illiquidity ratio (price impact per unit volume)
- Composite score combining both metrics via percentile ranking

### Volatility Factor
Economic rationale: Excessively volatile assets often exhibit unstable return patterns and may warrant lower portfolio weights.

Calculation:
- Annualized historical volatility (21-day rolling standard deviation)
- Parkinson volatility estimator using high-low price range
- Normalized such that lower volatility receives higher scores

---

## Asset Ranking and Scoring

For each analysis date, all assets receive normalized scores (0-100) for each factor based on their cross-sectional percentile rank. The final composite score is a weighted average:

Composite Score = (0.40 × Momentum Score) + (0.30 × Liquidity Score) + (0.30 × Inverse Volatility Score)

Assets are then classified into investment categories based on their composite score:

| Score Range      | Classification   |
|------------------|------------------|
| 80 - 100         | COMPRA FORTE     |
| 60 - 79          | COMPRA MODERADA  |
| 40 - 59          | NEUTRO           |
| 20 - 39          | EVITAR           |
| 0 - 19           | VENDA FORTE      |

---

## Portfolio Construction

The portfolio construction process follows deterministic rules without discretionary intervention. Assets classified as COMPRA FORTE or COMPRA MODERADA are eligible for inclusion.

### Allocation Rules
- Equal-weight allocation within each classification tier
- Maximum portfolio exposure: 80% of capital in equities
- Remaining capital held as cash reserve
- Long-only strategy (no short positions)

### Rebalancing Frequency
Portfolio rebalancing occurs monthly on predefined dates. At each rebalance:
- Expired signals are liquidated
- New signals are added based on updated factor scores
- Portfolio weights are reset to target allocations
- Transaction costs are applied to all trades

---

## Backtesting Engine

The backtesting framework simulates portfolio performance using historical data with realistic implementation constraints.

### Core Parameters
- Initial capital: R$ 100,000
- Benchmark: IBOVESPA index
- Time period: January 2023 to December 2023
- Rebalancing: Monthly (approximately 30-day intervals)
- Transaction cost: 0.05% per trade (execution + slippage)
- Cash yield: 0% (no interest on idle cash)
- Used Tickers : ITUB4.SA, BBDC4.SA, VALE3.SA, PETR4.SA, GGBR4.SA, BPAC11.SA, B3SA3.SA, PETR3.SA, BBAS3.SA, SANB11.SA,CSNA3.SA, ABEV3.SA

### Methodology
The simulation processes each rebalancing date sequentially:
1. Fetch current portfolio positions and cash balance
2. Retrieve latest factor scores for all assets
3. Identify assets to sell (no longer in top tiers)
4. Execute sales and update cash balance
5. Identify assets to buy (currently in top tiers)
6. Calculate target position sizes based on available cash
7. Execute purchases and update portfolio holdings
8. Record portfolio state and trade history
9. Calculate performance metrics for the period

All price lookups use the closing price on the rebalancing date, ensuring the simulation uses only information available at the time of decision.

---

## Performance Analysis

### Key Metrics
| Metric                    | Value              |
|---------------------------|--------------------|
| Initial Capital           | R$ 100,000         |
| Final Capital             | R$ 144,663         |
| Total Return              | +44.66%            |
| Number of Trades          | 24 transactions    |
| Final Number of Holdings  | 3 assets           |
| Benchmark Return (IBOV)   | +21.96%            |
| Excess Return (Alpha)     | +22.70 percentage points |

### Risk Metrics
- Maximum drawdown: Not exceeding 10% during the period
- Portfolio turnover: Moderate, with holdings concentrated in top-ranked assets
- Concentration: Final portfolio concentrated in highest-conviction signals

### Benchmark Comparison
The strategy consistently outperformed the IBOVESPA benchmark throughout the backtest period, with particularly strong relative performance during market rallies. The alpha generation appears driven by successful stock selection within the momentum and liquidity factors.

---

## Power BI Dashboard

The repository includes a comprehensive Power BI dashboard for interactive performance analysis:

### Dashboard Features
- Equity curve comparison (strategy vs IBOVESPA)
- Time-series of portfolio composition
- Factor score evolution for each asset
- Trade history and transaction analysis
- Monthly return attribution
- Risk metrics visualization

### File Location
dashboard/project-quant.pbix

A PDF export is also available for quick reference: dashboard/project-quant.pdf

---

## Repository Structure

```
quant-project/
│
├── api/                          # Data acquisition and backtesting
│   ├── market_data.py            # Yahoo Finance data fetcher
│   └── backtest.py               # Portfolio simulation engine
│
├── database/                      # Data persistence layer
│   ├── connection.py              # SQLite database handler
│   └── acoes.db                   # Price database (local)
│
├── factors/                       # Factor computation modules
│   ├── momentum.py                 # Momentum factor implementation
│   ├── liquidity.py                # Liquidity metrics (volume, Amihud)
│   ├── volatility.py               # Volatility estimators
│   └── returns.py                  # Factor consolidation and ranking
│
├── dashboard/                      # Performance visualization
│   ├── project-quant.pbix          # Power BI dashboard
│   └── project-quant.pdf           # Dashboard export
│
├── reports/                         # Backtest outputs
│   ├── backtest_resultado_*.xlsx   # Simulation results by date
│   └── relatorio_investimento.xlsx # Factor analysis reports
│
├── main.py                          # Orchestration script
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

---

## Technical Requirements

### Python Environment
- Python 3.11 or higher
- Dependencies listed in requirements.txt

### Key Libraries
- pandas: Data manipulation and analysis
- numpy: Numerical computations
- yfinance: Market data retrieval
- sqlite3: Local database storage
- openpyxl: Excel export functionality

### Installation
```bash
pip install -r requirements.txt
```

---

## Usage Instructions

### 1. Data Collection
```python
from api.market_data import DataFetcher

fetcher = DataFetcher()
fetcher.get_data()          # Preview downloaded data
fetcher.save_data()          # Store in database
```

### 2. Factor Analysis
```python
from factors.returns import executar_analise_completa

ranking = executar_analise_completa()
# Generates factor scores and recommendation report
```

### 3. Backtest Simulation
```python
from api.backtest import executar_backtest

simulador, historico = executar_backtest(
    saldo_inicial=100000,
    data_inicio="2023-01-01",
    data_fim="2024-01-01"
)
# Results saved to reports/ directory
```

---

## Methodological Considerations

### Factor Selection Rationale
The three factors were selected based on their theoretical foundations in financial economics and empirical evidence of their predictive power in emerging markets:

- Momentum captures behavioral biases and trend-following effects
- Liquidity addresses market microstructure and transaction costs
- Volatility reflects risk preferences and stability requirements

### Weighting Scheme
The 40/30/30 weight allocation reflects a higher conviction in momentum as a standalone predictor, while maintaining diversification across independent risk dimensions. Alternative weighting schemes can be tested in future iterations.

### Look-Ahead Bias Prevention
All calculations use only information available up to the analysis date. Rolling windows ensure that no future data contaminates historical signals. Price lookups in backtesting use the exact date of rebalancing.

### Transaction Costs
The 0.05% per trade assumption represents a conservative estimate for institutional execution costs in Brazilian equities, including brokerage fees, exchange fees, and estimated market impact.

---

## Limitations and Future Development

### Current Limitations
- Limited historical period (1 year of backtest data)
- Small universe of assets (12 major IBOVESPA constituents)
- No sector or industry adjustments
- Simple equal-weight allocation within tiers
- No risk management beyond volatility filtering

### Planned Enhancements

Factor Expansion:
- Value factors (P/E, P/B, dividend yield)
- Quality metrics (ROE, profit margins, earnings stability)
- Size factor (market capitalization)
- Sentiment indicators (options flow, short interest)

Risk Modeling:
- Volatility targeting and position sizing
- Maximum drawdown constraints
- Sector exposure limits
- Correlation-aware diversification

Methodology Improvements:
- Machine learning for factor weighting optimization
- Regime-switching models for factor timing
- Bayesian shrinkage for score estimation
- Cross-validation for parameter robustness

Infrastructure:
- Automated daily data pipeline
- Cloud database deployment
- Real-time signal generation
- Web-based dashboard interface

---

## Professional Disclaimer

This project is intended for educational and research purposes only. It does not constitute investment advice or a recommendation to buy or sell any financial instrument. The strategies and analyses presented herein are based on historical data and hypothetical assumptions that may not reflect actual market conditions.

Past performance is not indicative of future results. Any investment decision should be based on thorough due diligence and consideration of individual risk tolerance and investment objectives. The authors assume no responsibility for any financial losses incurred from the use of this research.

---

## Contact and Contributions

This project represents a quantitative research initiative in systematic equity strategies. For questions, suggestions, or collaboration opportunities, please refer to the repository issues page or contact the repository maintainer directly.

Contributions that enhance the methodological rigor, expand the factor universe, or improve the backtesting infrastructure are welcome and encouraged.
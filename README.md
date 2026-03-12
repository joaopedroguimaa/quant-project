# Quantitative Equity Strategy – Brazil (B3)

## Project Overview
This repository implements a systematic equity investment strategy for the Brazilian market (B3).  The end‑to‑end pipeline collects market data, stores it in a relational database, computes factor scores, ranks assets, constructs a monthly‑rebalanced portfolio, and backtests performance against the IBOVESPA benchmark.  Results are visualized in a Power BI dashboard for stakeholder communication.

## Strategy Philosophy
The strategy follows a **factor‑based, long‑only, moderate‑risk** approach.  By combining momentum, volatility, liquidity, and returns‑based scoring, the model seeks to capture persistent risk premia while controlling turnover and exposure.  Asset selection is performed monthly, aligning with typical institutional rebalancing cycles.

## Data Pipeline Architecture
1. **Market Data Collection** – Daily price and volume data are retrieved via `yfinance`.
2. **Storage** – Raw data are persisted in a SQL database (PostgreSQL) to enable reproducible queries and incremental updates.
3. **Factor Calculation** – Custom Python modules compute the four factors (momentum, volatility, liquidity, returns).
4. **Ranking Model** – Assets are ranked on a composite score derived from the factor values.
5. **Portfolio Construction** – The top‑ranked assets are allocated to two buckets: *Compra Moderada* (moderate exposure) and *Compra Forte* (high conviction).
6. **Backtesting** – Monthly rebalancing is simulated; performance is compared to the IBOVESPA index.

## Factor Model
| Factor | Description | Implementation Highlights |
|--------|-------------|---------------------------|
| Momentum | Recent price appreciation over the past 12 months. | Uses cumulative returns, adjusted for dividends. |
| Volatility | Historical price variability. | Annualized standard deviation of daily returns. |
| Liquidity | Market depth and tradability. | Average daily traded volume over the past 60 days. |
| Returns‑Based Scoring | Absolute performance metric. | Mean monthly return over the past 6 months. |

## Portfolio Construction
- **Selection** – Assets are sorted by the composite factor score.
- **Buckets** – The top 10 % are placed in *Compra Forte* (higher weight), the next 20 % in *Compra Moderada*.
- **Weighting** – Equal‑weight within each bucket; total exposure capped at 80 % of capital.
- **Rebalancing** – Executed on the first trading day of each month.

## Backtesting Methodology
- **Time Horizon** – January 2020 to December 2024 (5 years).
- **Benchmark** – IBOVESPA total‑return index.
- **Metrics** – Total return, annualized return, volatility, Sharpe ratio, and alpha relative to the benchmark.
- **Transaction Costs** – Assumed 0.05 % per trade to reflect realistic market impact.

## Results
| Metric | Value |
|--------|-------|
| Initial Capital | R$ 100,000 |
| Final Capital | R$ 147,010 |
| Total Return | **+47.01 %** |
| Annualized Return | 8.5 % |
| Annualized Volatility | 12.3 % |
| Sharpe Ratio | 0.61 |
| Alpha vs IBOVESPA | +2.4 % |

The strategy outperforms the benchmark on a risk‑adjusted basis, delivering positive alpha over the full sample period.

## Dashboard Visualization
A Power BI dashboard (included in the `dashboard/` folder) presents:
- Monthly portfolio equity curve vs. IBOVESPA.
- Turnover and exposure statistics.
- Interactive drill‑throughs for individual asset performance.

## Tech Stack
- **Language**: Python 3.11
- **Data Retrieval**: `yfinance`
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Numerical Computing**: `pandas`, `numpy`
- **Statistical Modeling**: `scipy`, `statsmodels`
- **Backtesting**: Custom engine built on `pandas`
- **Visualization**: Power BI (desktop file provided)
- **Version Control**: Git (GitHub)

## Repository Structure
```
├─ README.md                # Project documentation (this file)
├─ main.py                  # Entry point for pipeline execution
├─ api/                     # Data acquisition and backtesting APIs
│   ├─ market_data.py       # yfinance wrapper and DB loader
│   └─ backtest.py          # Backtesting engine
├─ factors/                 # Factor calculation modules
│   ├─ momentum.py
│   ├─ volatility.py
│   ├─ liquidity.py
│   └─ returns.py
├─ db/                      # Database schema and connection utilities
│   └─ connection.py        # Get Data 
├─ reports/                 # Backtest output files (CSV/Excel)
├─ dashboard/               # Power BI dashboard files
└─ requirements.txt        # Python dependencies
```

## Future Improvements
- **Expanded Factor Universe** – Incorporate macro‑economic and sentiment indicators.
- **Machine‑Learning Ranking** – Replace linear composite scoring with a regularized regression or gradient‑boosting model.
- **Risk Management** – Implement VaR‑based position limits and dynamic volatility scaling.
- **Live Deployment** – Transition from backtesting to a production‑grade pipeline using Airflow/Kedro.

## Disclaimer
The code and analyses provided are for **educational purposes only** and do not constitute investment advice.  Past performance is not indicative of future results.  Users should conduct their own due diligence before employing any trading strategy.

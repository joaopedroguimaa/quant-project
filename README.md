# Quantitative Multi-Factor Equity Strategy — Brazilian Market (B3)

## Overview

This project implements a **systematic quantitative equity strategy** for the Brazilian stock market (B3). The repository contains an end-to-end research pipeline covering **data acquisition, factor modeling, portfolio construction, and backtesting** against the IBOVESPA benchmark.

The objective is to evaluate whether a **multi-factor ranking model** based on market characteristics (momentum, volatility, liquidity, and return persistence) can generate **risk-adjusted excess returns** relative to the benchmark.

The project also includes a **Power BI dashboard** used to visualize portfolio performance and asset-level signals.

---

## Research Motivation

Systematic equity strategies attempt to capture **persistent factor premia** observed in financial markets.

This project explores a **cross-sectional factor model** applied to Brazilian equities, where assets are ranked according to a composite score derived from multiple signals.

The hypothesis tested:

> Assets exhibiting favorable combinations of momentum, liquidity, and return persistence while maintaining moderate volatility may outperform the broader market over time.

The strategy follows a **rules-based portfolio construction process**, avoiding discretionary decisions.

---

## Quantitative Pipeline

The strategy pipeline is structured into the following stages:

1. **Market Data Collection**
2. **Data Storage**
3. **Factor Computation**
4. **Cross-Sectional Ranking**
5. **Portfolio Construction**
6. **Backtesting**
7. **Performance Visualization**

Workflow:

Market Data → Database → Factor Engine → Asset Ranking → Portfolio Construction → Backtest → Dashboard

---

## Data Source

Market data is retrieved using:

* `yfinance`

Data collected includes:

* Daily adjusted close prices
* Trading volume
* Historical returns

Assets correspond to **major IBOVESPA constituents and liquid B3 equities**.

---

## Factor Model

The model combines four independent factors representing common drivers of equity returns.

| Factor             | Economic Intuition                                                                                | Implementation                                 |
| ------------------ | ------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Momentum           | Assets with positive past performance tend to continue outperforming in the short-to-medium term. | 12-month cumulative return                     |
| Volatility         | Extremely volatile assets often exhibit unstable returns.                                         | Annualized standard deviation of daily returns |
| Liquidity          | Highly traded stocks are easier to enter and exit without price impact.                           | Average traded volume (60-day window)          |
| Return Persistence | Consistent positive returns may indicate underlying strength.                                     | Average monthly return (6-month window)        |

Each asset receives a **normalized score** for every factor.
The final ranking score is computed as a **composite factor score**.

---

## Portfolio Construction

Portfolio allocation follows a deterministic selection process.

Selection logic:

* Assets ranked by composite factor score
* Top-ranked assets classified into two conviction tiers

Allocation rules:

| Bucket          | Description                |
| --------------- | -------------------------- |
| Compra Forte    | Highest conviction signals |
| Compra Moderada | Moderate positive signals  |

Portfolio characteristics:

* Equal weight inside each bucket
* Maximum capital exposure: 80%
* Monthly rebalancing
* Long-only strategy

---

## Backtesting Methodology

The backtesting engine simulates historical portfolio performance using a **monthly rebalancing schedule**.

Key assumptions:

| Parameter             | Value           |
| --------------------- | --------------- |
| Time Period           | 2020 — 2024     |
| Initial Capital       | R$100,000       |
| Benchmark             | IBOVESPA        |
| Rebalancing Frequency | Monthly         |
| Transaction Cost      | 0.05% per trade |

Performance metrics calculated:

* Total Return
* Annualized Return
* Annualized Volatility
* Sharpe Ratio
* Alpha vs Benchmark

---

## Strategy Performance

| Metric            | Result      |
| ----------------- | ----------- |
| Initial Capital   | R$100,000   |
| Final Capital     | R$147,010   |
| Total Return      | **+47.01%** |
| Annualized Return | 8.5%        |
| Volatility        | 12.3%       |
| Sharpe Ratio      | 0.61        |
| Alpha vs IBOVESPA | +2.4%       |

The results suggest **positive risk-adjusted performance relative to the benchmark** during the analyzed period.

---

## Dashboard

The project includes a **Power BI dashboard** for performance analysis.

Location:

dashboard/Multifactors Quant Strategy.pbix

Dashboard features:

* Portfolio equity curve vs IBOVESPA
* Asset-level signal visualization
* Factor ranking overview
* Portfolio allocation snapshots

---

## Tech Stack

Language
Python 3.11

Data & Numerical Computing

* pandas
* numpy

Data Retrieval

* yfinance

Database

* PostgreSQL
* SQLAlchemy

Backtesting

* Custom pandas-based engine

Visualization

* Power BI

Version Control

* Git / GitHub

---

## Repository Structure

```
quant-project
│
├── api
│   ├── market_data.py
│   └── backtest.py
│
├── database
│   ├── connection.py
│   └── acoes.db
│
├── factors
│   ├── momentum.py
│   ├── volatility.py
│   ├── liquidity.py
│   └── returns.py
│
├── dashboard
│   └── Multifactors Quant Strategy.pbix
│
├── reports
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Potential Improvements

Future iterations of the project may include:

Factor Expansion

* Value factors (P/E, P/B)
* Quality factors (ROE, margins)
* Size factor

Risk Modeling

* Volatility targeting
* Drawdown control
* Position constraints

Machine Learning Extensions

* Gradient boosting ranking models
* Regularized regression for factor weighting

Production Pipeline

* Scheduled data ingestion
* Automated rebalancing pipeline
* Research framework integration (Airflow / Prefect)

---

## Disclaimer

This repository is intended for **educational and research purposes only**.
It does not constitute financial advice or a recommendation to buy or sell securities.

Past performance does not guarantee future results.

---

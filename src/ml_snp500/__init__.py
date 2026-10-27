import warnings

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", module="yfinance")


def load_sp500(start="1990-01-01") -> pd.DataFrame:
   df = yf.Ticker("^GSPC").history(period="max")
   df = df.drop(columns=["Dividends", "Stock Splits"], errors="ignore")
   df["Tomorrow"] = df["Close"].shift(-1)
   df["Target"] = (df["Tomorrow"] > df["Close"]).astype(int)
   return df.loc[start:].copy()


def add_horizon_features(df: pd.DataFrame, horizons=(2, 5, 60, 250, 1000)):
   new_predictors = []
   for horizon in horizons:
      rolling = df.rolling(horizon).mean()
      ratio = f"Close_Ratio_{horizon}"
      trend = f"Trend_{horizon}"
      df[ratio] = df["Close"] / rolling["Close"]
      df[trend] = df.shift(1).rolling(horizon).sum()["Target"]
      new_predictors += [ratio, trend]
   return df.dropna(), new_predictors


def predict(train, test, predictors, model, threshold=0.6):
   model.fit(train[predictors], train["Target"])
   preds = model.predict_proba(test[predictors])[:, 1]
   preds = (preds >= threshold).astype(int)
   return pd.concat(
      [test["Target"], pd.Series(preds, index=test.index, name="Predictions")],
      axis=1,
   )


def backtest(data, model, predictors, start=2500, step=250):
   chunks = []
   for i in range(start, data.shape[0], step):
      train = data.iloc[:i].copy()
      test = data.iloc[i : i + step].copy()
      chunks.append(predict(train, test, predictors, model))
   return pd.concat(chunks)


def main():
   sp500 = load_sp500()
   sp500.plot.line(y="Close", use_index=True)
   plt.savefig("sp500_close.png")
   plt.close()

   # First model (raw OHLCV, last 100-day holdout) — optional
   predictors = ["Close", "Volume", "Open", "High", "Low"]
   model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
   train, test = sp500.iloc[:-100], sp500.iloc[-100:]
   model.fit(train[predictors], train["Target"])
   holdout = model.predict(test[predictors])
   print("holdout precision:", precision_score(test["Target"], holdout))

   # Improved model (ratios + trends + 0.6 threshold)
   sp500, new_predictors = add_horizon_features(sp500)
   model = RandomForestClassifier(n_estimators=200, min_samples_split=50, random_state=1)
   predictions = backtest(sp500, model, new_predictors)
   print(predictions["Predictions"].value_counts())
   print("backtest precision:", precision_score(predictions["Target"], predictions["Predictions"]))
   predictions.plot()
   plt.savefig("predictions.png")
   plt.close()


if __name__ == "__main__":
   main()
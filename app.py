import io, base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from scipy.optimize import curve_fit

st.set_page_config(page_title="IC50 Explorer", layout="wide")
st.title("IC50 Explorer • 4-Parameter Logistic (4PL)")

st.write("Upload a CSV with columns: **sample, concentration, response** (concentration > 0). "
         "App fits a 4PL curve per sample and reports EC50, Hill, and R².")

# Example data (used if you don't upload a file)
sample_csv = pd.DataFrame({
    "sample": ["drugA"]*8 + ["drugB"]*8,
    "concentration": np.r_[np.logspace(-2, 2, 8), np.logspace(-2, 2, 8)],
    "response": np.r_[ [98,96,90,70,45,25,12,8], [99,98,95,90,80,70,62,58] ]
})
def df_bytes(df): return df.to_csv(index=False).encode()

with st.expander("Need an example CSV?"):
    st.dataframe(sample_csv.head(8))
    st.download_button("Download example.csv", df_bytes(sample_csv), "example.csv", "text/csv")

uploaded = st.file_uploader("Upload your CSV", type=["csv"])
data = pd.read_csv(uploaded) if uploaded else sample_csv.copy()

def four_pl(x, bottom, top, logEC50, hill):
    return bottom + (top-bottom) / (1 + (10**(logEC50 - np.log10(x)))**hill)

def fit_group(g):
    x = g["concentration"].astype(float).to_numpy()
    y = g["response"].astype(float).to_numpy()
    if np.any(x <= 0): raise ValueError("Concentration must be > 0.")
    p0 = [y.min(), y.max(), np.log10(np.median(x)), 1.0]
    popt, _ = curve_fit(four_pl, x, y, p0=p0, maxfev=20000)
    yhat = four_pl(x, *popt)
    r2 = 1 - ((y - yhat)**2).sum() / (((y - y.mean())**2).sum() + 1e-12)
    return popt, r2

results, plots = [], []
for sample, g in data.groupby("sample"):
    try:
        popt, r2 = fit_group(g)
        bottom, top, logEC50, hill = popt
        EC50 = 10**logEC50
        results.append([sample, EC50, hill, r2, bottom, top])

        xs = np.logspace(np.log10(g.concentration.min()/3),
                         np.log10(g.concentration.max()*3), 200)
        fig, ax = plt.subplots()
        ax.semilogx(g.concentration, g.response, 'o', label="data")
        ax.semilogx(xs, four_pl(xs, *popt), '-', label="4PL fit")
        ax.set_xlabel("Concentration"); ax.set_ylabel("Response")
        ax.set_title(f"{sample}  R²={r2:.3f}  EC50={EC50:.3g}")
        ax.legend()
        plots.append(fig)
    except Exception as e:
        results.append([sample, np.nan, np.nan, np.nan, np.nan, np.nan])
        st.warning(f"Fit failed for {sample}: {e}")

if results:
    dfres = pd.DataFrame(results, columns=["sample","EC50","Hill","R2","bottom","top"])
    st.subheader("Results")
    st.dataframe(dfres, use_container_width=True)
    st.download_button("Download results.csv", df_bytes(dfres), "results_ic50.csv", "text/csv")
    st.subheader("Fits")
    cols = st.columns(2)
    for i, fig in enumerate(plots):
        with cols[i % 2]:
            st.pyplot(fig)

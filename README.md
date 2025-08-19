# IC50 Explorer · 4-Parameter Logistic (4PL)

**Live demo:** <https://YOUR-APP-URL.streamlit.app>  
**Tech:** Streamlit · Python · NumPy · SciPy · Matplotlib

Small web app that fits **4PL dose–response curves** and reports **EC50**, **Hill slope**, and **R²** per sample.

## How to use
1. Prepare a CSV with columns: `sample, concentration, response` (concentration > 0).
2. Open the live demo and upload the CSV (or try the example in the app).
3. Download the results table and per-sample plots.

### CSV schema (example)
```csv
sample,concentration,response
drugA,0.01,98
drugA,0.1,90
drugA,1,45
drugA,10,12
drugB,0.01,99
drugB,0.1,95
drugB,1,80
drugB,10,62

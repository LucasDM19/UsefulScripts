"""
Artigo: https://medium.com/@ageitgey/quick-tip-the-easiest-way-to-grab-data-out-of-a-web-page-in-python-7153cecfca58
"""

import pandas as pd

calls_df, = pd.read_html("http://apps.sandiego.gov/sdfiredispatch/", header=0, parse_dates=["Call Date"])

print(calls_df.to_json(orient="records", date_format="iso"))
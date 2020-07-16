"""
Artigo: https://medium.com/@ageitgey/quick-tip-the-easiest-way-to-grab-data-out-of-a-web-page-in-python-7153cecfca58
"""

import pandas as pd

tables = pd.read_html("https://apps.sandiego.gov/sdfiredispatch/")

print(tables[0])
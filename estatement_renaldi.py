# 1. Install required packages
# !pip install pymupdf pandas

# 2. Import necessary libraries
import fitz  # PyMuPDF
import pandas as pd
import re

# 3. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 4. Load PDF
pdf_path = '/content/drive/My Drive/ebs/april_banjar.pdf'
doc = fitz.open(pdf_path)
text = ""
for page in doc:
    text += page.get_text()

# 5. Regex to capture all ref_no starting with '000'
pattern = re.compile(
    r'(?P<ref_no>000[A-Z0-9]+)\s+'
    r'(?P<trn_date>\d{2}-\w{3}-\d{4})\s+'
    r'(?P<eff_date>\d{2}-\w{3}-\d{4})\s+'
    r'(?P<amount>[0-9,]+\.\d{2})\s+'
    r'(?P<balance>[0-9,]+\.\d{2})'
)

# 6. Capture all matches
matches = list(pattern.finditer(text))

# 7. Initialize list to hold parsed data
records = []

# 8. Parse and calculate type by comparing balance with previous balance
prev_balance = None
for i, match in enumerate(matches):
    data = match.groupdict()
    balance = float(data['balance'].replace(',', ''))
    amount = float(data['amount'].replace(',', ''))
    
    txn_type = ''
    if prev_balance is not None:
        txn_type = 'CREDIT' if balance > prev_balance else 'DEBIT'
    else:
        txn_type = 'INIT'
    
    # Extract description manually (up to next ref_no or EOF)
    desc_start = match.end()
    desc_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    description = text[desc_start:desc_end].replace('\n', ' ').strip()
    description = re.sub(r'\s{2,}', ' ', description)  # Clean up excessive spaces

    records.append({
        'ref_no': data['ref_no'],
        'trn_date': data['trn_date'],
        'eff_date': data['eff_date'],
        'amount': amount,
        'balance': balance,
        'type': txn_type,
        'description': description
    })

    prev_balance = balance

# 9. Convert to DataFrame and adjust order
df = pd.DataFrame(records)
df = df[['ref_no', 'trn_date', 'eff_date', 'amount', 'balance', 'type', 'description']]

# 10. Save to CSV
output_path = '/content/drive/My Drive/ebs/april_banjar_output_balanced.csv'
df.to_csv(output_path, index=False)

# 11. Show preview
print(f"✅ Saved to: {output_path}")
df.head()

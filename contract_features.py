import pandas as pd
import json
from datetime import datetime, timedelta

# Function to calculate the tot_claim_cnt_l180d 
def calculate_tot_claim_cnt_l180d(application_date, contracts):
    count = 0
    # Parse the application_date with timezone (no conversion needed)
    application_date = datetime.strptime(application_date, "%Y-%m-%d %H:%M:%S.%f%z")  # Handles any timezone dynamically
    
    for contract in contracts:
        try:
            claim_date = datetime.strptime(contract.get('claim_date', ''), "%d.%m.%Y")
            if claim_date and (application_date - claim_date).days <= 180:
                count += 1
        except ValueError:
            continue
    return count if count > 0 else -3

# Function to calculate the disb_bank_loan_wo_tbc
def calculate_disb_bank_loan_wo_tbc(contracts):
    total_sum = 0
    excluded_banks = ['LIZ', 'LOM', 'MKO', 'SUG', None]
    for contract in contracts:
        try:
            bank = contract.get('bank', '')
            loan_summa = contract.get('loan_summa', '')
            contract_date = contract.get('contract_date', '')
            
            # Consider loan if bank is not in excluded list and contract_date is not empty
            if bank not in excluded_banks and loan_summa and contract_date:
                total_sum += float(loan_summa)
        except ValueError:
            continue
    return total_sum if total_sum > 0 else -1

# Function to calculate the day_sinlastloan 
def calculate_day_sinlastloan(application_date, contracts):
    last_loan_date = None
    # Parse the application_date with timezone (no conversion needed)
    application_date = datetime.strptime(application_date, "%Y-%m-%d %H:%M:%S.%f%z")  # Handles any timezone dynamically
    
    for contract in contracts:
        try:
            loan_summa = contract.get('summa', '')
            contract_date = contract.get('contract_date', '')
            
            if loan_summa and contract_date:
                loan_date = datetime.strptime(contract_date, "%d.%m.%Y")
                if last_loan_date is None or loan_date > last_loan_date:
                    last_loan_date = loan_date
        except ValueError:
            continue
    
    if last_loan_date is None:
        return -1
    
    return (application_date - last_loan_date).days

# Read the CSV file
df = pd.read_csv('C:/Users/ASUS/Desktop/data')


# Initialize lists to store the calculated features
tot_claim_cnt_l180d_list = []
disb_bank_loan_wo_tbc_list = []
day_sinlastloan_list = []

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    # Parse the contracts JSON string
    contracts = json.loads(row['contracts']) if isinstance(row['contracts'], str) else []
    
    # Calculate features
    tot_claim_cnt_l180d_value = calculate_tot_claim_cnt_l180d(row['application_date'], contracts)
    disb_bank_loan_wo_tbc_value = calculate_disb_bank_loan_wo_tbc(contracts)
    day_sinlastloan_value = calculate_day_sinlastloan(row['application_date'], contracts)
    
    # Append the calculated features to the lists
    tot_claim_cnt_l180d_list.append(tot_claim_cnt_l180d_value)
    disb_bank_loan_wo_tbc_list.append(disb_bank_loan_wo_tbc_value)
    day_sinlastloan_list.append(day_sinlastloan_value)

# Add the new features to the dataframe
df['tot_claim_cnt_l180d'] = tot_claim_cnt_l180d_list
df['disb_bank_loan_wo_tbc'] = disb_bank_loan_wo_tbc_list
df['day_sinlastloan'] = day_sinlastloan_list

# Save the resulting dataframe to a new CSV file
df.to_csv('contract_features.csv', index=False)

print("job is done") 


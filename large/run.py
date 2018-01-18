from decimal import *

from finance import Bank, Facility, Covenant, Loan
from helpers import read_csv, write_csv

# Read the csv file from banks.csv and generate bank dictionary
banks_rows = read_csv('banks.csv')
banks = {}
for row in banks_rows:
    bank_id = int(row[0])
    bank_name = row[1]
    bank = Bank(bank_id, bank_name)
    banks[bank.bank_id] = bank

# Read the csv file from facilities.csv and assign facilities to banks
facilities_rows = read_csv('facilities.csv')
for row in facilities_rows:
    facility_id = int(row[2])
    bank_id = int(row[3])
    interest_rate = Decimal(row[1])
    amount = Decimal(row[0])
    facility = Facility(facility_id, bank_id, interest_rate, amount)
    banks[facility.bank_id].facilities[facility_id] = facility

# Read the csv file from covenants.csv and assign covenants to banks or facilities
covenants_rows = read_csv('covenants.csv')
for row in covenants_rows:

    bank_id = int(row[2])

    if row[0] is not None and len(row[0]) > 0:
        facility_id = int(row[0])
    else:
        facility_id = None

    if row[1] is not None and len(row[1]) > 0:
        max_default_likelihood = Decimal(row[1])
    else:
        max_default_likelihood = None

    if row[3] is not None and len(row[3]) > 0:
        banned_state = row[3]
    else:
        banned_state = None

    # If 2 values state and default create 2 covenants
    # Otherwise create 1 covenant per row
    if banned_state and max_default_likelihood:
        covenant1 = Covenant(
            bank_id, max_default_likelihood=max_default_likelihood,
            facility_id=facility_id
        )
        covenant2 = Covenant(
            bank_id, facility_id=facility_id, banned_state=banned_state)

        # If facility id exists locate and assign to the proper facility
        # Otherwise assign the covenant to the bank as a whole
        if facility_id:
            bank = banks[bank_id]
            bank.facilities[facility_id].covenants.append(covenant1)
            bank.facilities[facility_id].covenants.append(covenant2)
        else:
            banks = banks[bank_id]
            bank.covenants.append(covenant1)
            bank.covenants.append(covenant2)

    else:

        covenant = Covenant(
            bank_id, max_default_likelihood=max_default_likelihood,
            facility_id=facility_id, banned_state=banned_state
        )

        if facility_id:
            bank = banks[bank_id]
            bank.facilities[facility_id].covenants.append(covenant)
        else:
            banks = banks[bank_id]
            bank.covenants.append(covenant)

# Read the csv file from loans.csv do line by line to imitate stream
# create a dictionary mapping loans to facilities
# Calculate yield and update facility yield for each loan
facilities_loans_assignment = {}
loans_rows = read_csv('loans.csv')
for row in loans_rows:

    # Default facility id assigned is none
    cheapest_facility = None

    # Create loan object
    loan_id = int(row[2])
    amount = int(row[1])
    interest_rate = Decimal(row[0])
    default_likelihood = Decimal(row[3])
    state = row[4]
    loan = Loan(loan_id, amount, interest_rate, default_likelihood, state)

    # Iterate through banks
    for bank_id, bank in banks.iteritems():
        valid_bank = True

        # If there are covenants in the bank validate covenant against loan
        # if invalid covenant then break and move to next bank
        if len(bank.covenants) > 0:
            for covenant in bank.covenants:
                if not covenant.valid_loan(loan):
                    valid_bank = False
                    break
            if not valid_bank:
                continue

        # Covenant for bank has been validated so now must validate against facilities
        for facility_id, facility in bank.facilities.iteritems():
            valid_facility = True

            # Check if facility has enough money
            if not facility.valid_loan(loan):
                valid_facility = False
                continue
            else:

                # Iterate through each covenant in a facility
                # If there is an invalid covenant then break and invalidate current facility
                for covenant in facility.covenants:
                    if not covenant.valid_loan(loan):
                        valid_facility = False
                        break

            # If facility is valid check if it is cheaper than the current facility
            # If None assign automatically
            if valid_facility:
                if cheapest_facility is None:
                    cheapest_facility = facility
                else:
                    if cheapest_facility.interest_rate > facility.interest_rate:
                        cheapest_facility = facility

    # Update the expected_yield and amount for the facility once a loan has been assigned
    # if the facility is not None
    if cheapest_facility is not None:
        cheapest_facility.update_expected_yield_and_amount(loan)
    facilities_loans_assignment[loan_id] = cheapest_facility.facility_id

facility_yields = {}
for bank_id, bank in banks.iteritems():
    for facility_id, facility in bank.facilities.iteritems():
        facility_yields[facility_id] = round(facility.expected_yield)

write_csv('assignment.csv', ['load_id', 'facility_id'], facilities_loans_assignment)
write_csv('yields.csv', ['facility_id', 'expected_yield'], facility_yields)

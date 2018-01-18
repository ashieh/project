"""
    assignment_code.models.finance

    Loan, Bank, Facility, Covenant model
"""

"""
Bank Class

parameters
bank_id: integer
bank_name: string

Takes a bank id and bank name on instantiation. Facilities are initailized as empty
dictionaries to track by facility_id and Covenants are initiailized as
empty arrays and assigned when reading from the facilities.csv and covenants.csv.
"""
class Bank:

    def __init__(self, bank_id, bank_name):
        self.bank_id = bank_id
        self.bank_name = bank_name
        self.facilities = {}
        self.covenants = []


"""
Facility Class

parameters
bank_id: integer
facility_id: integer
interest_rate: decimal
amount: integer

Takes a bank id, facility_id, interest_rate, and amount on instantiation.
Covenants are initiailized as empty arrays and assigned when reading from covenants.csv.
"""

class Facility:

    def __init__(self, facility_id, bank_id, interest_rate, amount):
        self.facility_id = facility_id
        self.bank_id = bank_id
        self.interest_rate = interest_rate
        self.amount = amount
        self.covenants = []
        self.expected_yield = 0

    def update_expected_yield_and_amount(self, loan):
        expected_yield = ((1 - loan.default_likelihood) * loan.interest_rate * loan.amount -
            loan.default_likelihood * loan.amount - self.interest_rate * loan.amount)
        self.expected_yield = self.expected_yield + expected_yield
        self.amount = self.amount - loan.amount

    def valid_loan(self, loan):
        return self.amount > loan.amount


"""
Covenant Class

parameters
bank_id: integer
facility_id: integer
banned_state: string


Takes a bank_id and possibly a facility_id, and one of either banned_state or
max_default_likelihood.
"""
class Covenant:

    def __init__(self, bank_id, max_default_likelihood=None, facility_id=None, banned_state=None):
        self.bank_id = bank_id
        self.facility_id = facility_id
        self.max_default_likelihood = max_default_likelihood
        self.banned_state = banned_state

    def valid_loan(self, loan):
        if self.max_default_likelihood:
            return self.max_default_likelihood >= loan.default_likelihood
        else:
            return self.banned_state != loan.state

"""
Loan Class

parameters
id: integer
amount: integer
interest_rate: decimal
default_likelihood: decimal
state: string
"""

class Loan:
    def __init__(self, id, amount, interest_rate, default_likelihood, state):
        self.id = id
        self.amount = amount
        self.interest_rate = interest_rate
        self.default_likelihood = default_likelihood
        self.state = state

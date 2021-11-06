import requests
from config import URL

class RealTimeCurrencyConverter():
    def __init__(self, url):
        self.data = requests.get(url).json()
        self.currencies = self.data['rates']
    
    def convert(self, from_currency, to_currency, amount):
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]
        amount = round(amount * self.currencies[to_currency], 2)
        return amount
    
    def show_exrate(self, currencies):
        res = []
        for c in currencies:
            res.append(self.currencies[c])
        return res
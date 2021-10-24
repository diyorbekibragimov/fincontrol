import requests
from config import URL

class RealTimeCurrencyConverter():
    def __init__(self, url):
        self.data = requests.get(url).json()
        self.currencies = self.data['rates']
    
    def convert(self, from_currency, to_currency, amount):
        initial_amount = amount
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]
        amount = round(amount * self.currencies[to_currency], 2)
        return amount

if __name__ == '__main__':
    converter = RealTimeCurrencyConverter(URL)
    print(converter.convert("USD", "UZS", 2))
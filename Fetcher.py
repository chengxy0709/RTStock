import requests
import re

class Fetcher:
	def __init__(self):	 
		self.headers = {
			'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
		}

	def get_quotation(self, market : str, code : str) -> dict:
		url = 'http://hq.sinajs.cn/list=%s%s' % (market, code)
		try:
			rsp = requests.get(url, headers=self.headers)
			rsp = rsp.text.split('=')[1].strip('";\n').split(',')
			rsp = { 'name' : rsp[0],
					'open' : rsp[1],
					'close' : rsp[2],
					'price' : rsp[3],
					'high' : rsp[4],
					'low' : rsp[5],
					'bidding_buy' : rsp[6],
					'bidding_sell' : rsp[7],
					'count' : rsp[8],
					'amount' : rsp[9],
					'quote_buy' : rsp[10:20],
					'quote_sell' : rsp[20:30],
					'date' : rsp[30],
					'time' : rsp[31]
			}
			return rsp
		except Exception:
			print("check your network")
			return {}

	def get_market_and_code(self, name : str):
		url = 'https://suggest3.sinajs.cn/suggest/key=%s' % name
		try:
			rsp = requests.get(url, headers=self.headers)
			rsp = re.search('[a-z]{2}[0-9]{6}', rsp.text)

			if rsp:		
				return (rsp.group()[:2], rsp.group()[2:])
			else:
				return None
		except Exception:
			print("check your network")
			return None

# for testing Fetcher
if __name__ == '__main__':
	fetcher = Fetcher()
	print( fetcher.get_quotation('sh', '600519') )
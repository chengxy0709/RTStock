import os

class OptionalStock(object):
	def __init__(self, record : str):
		self.stocks = []

		# if record doesn't exist, generate it.
		if not os.path.exists(record):
			f = open(record, 'w')
			f.close()

		with open(record, mode = 'r') as f:
			self.recordFile = record # the file that stores all code of optional stocks
			line = f.readline()
			while line: # read a optional stock, format: market,code
				stock = list(map(lambda x : x.strip(), line.split(',')))
				if len(stock) == 2:
					self.stocks.append({'market' : stock[0],
										'code' : stock[1],
										'key' : None})
				line = f.readline()

	def add_stock(self, market : str, code : str) -> None:
		print()
		with open(self.recordFile, mode = 'a') as f:
			f.write('\n%s, %s' % (market, code)) # store this stock in the file

		self.stocks.append({'market' : market,
							'code' : code,
							})

	def top_stock(self, row):
		self.stocks = [self.stocks[row]] + self.stocks[:row] + self.stocks[(row + 1):]
		# update the file record
		with open(self.recordFile, mode = 'w') as f:
			for stock in self.stocks:
				f.write('%s, %s\n' % (stock['market'], stock['code']))

	def del_stock(self, row):
		del self.stocks[row]
		# update the file record
		with open(self.recordFile, mode = 'w') as f:
			for stock in self.stocks:
				f.write('%s, %s\n' % (stock['market'], stock['code']))

	def sort_stock(self, reverse = False):
		def sort_method(elem):
			return elem['key']
		self.stocks.sort(key = sort_method, reverse=reverse)
		with open(self.recordFile, mode = 'w') as f:
			for stock in self.stocks:
				f.write('%s, %s\n' % (stock['market'], stock['code']))
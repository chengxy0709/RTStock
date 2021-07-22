import sys
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5.QtWidgets import QLabel, QTableWidget, QHBoxLayout 
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QInputDialog
from PyQt5.QtWidgets import QPushButton
from functools import partial
from PyQt5.QtCore import QTimer
from Fetcher import Fetcher
from OptionalStock import OptionalStock

def stock_rate(price : float, close : float) -> str:
	""" return a percentage of rate """
	rate = (price - close) / close

	return "%.2f%%" % (rate * 100)

class Window(QWidget):
	"""docstring for Window"""
	def __init__(self, screen_width, screen_height, window_width, window_height):
		super().__init__()
		self.setGeometry(QRect(	screen_width / 2 - window_width / 2,
								screen_height / 2 - window_height / 2,
								window_width,
								window_height
								))
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.window_width = self.frameGeometry().width()
		self.window_height = self.frameGeometry().height()

		self.hidden = False # The window has not been hidden.
		self.stocks = OptionalStock('./record')
		self.stockTable = self.stocks.stocks # point to stocks in self.stocks

		self.initUI()

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_table_view_data)
		self.tick = 3000 # time tick is 3 seconds
		self.timer.start(self.tick) # start timer

	def initUI(self):
		self.setWindowTitle('RTStock') # set title
		self.move(100, 100) # modify the position of window
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # remove frame and keep it always at the top
		self.setWindowOpacity(0.8) # set the transparency of the window
		self.setCursor(Qt.PointingHandCursor) # set the style of the cursor

		# the header of window (a label)
		self.HeadView = QLabel('RT Stock',self)
		self.HeadView.setAlignment(Qt.AlignCenter)
		self.HeadView.setGeometry(QRect(0, 0, self.window_width, 25))
		self.HeadView.setFont(QFont("Roman times",12,QFont.Bold))

		# the body of window (a table)		
		self.stockTableView = QTableWidget(self)
		self.stockTableView.setGeometry(QRect(0, 40, self.window_width, 220))
		self.stockTableView.verticalHeader().setVisible(False)  # remove the vertical header of the table
		self.stockTableView.setEditTriggers(QAbstractItemView.NoEditTriggers) # disable editing
		self.stockTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # let the size of horizontal header of the table stretch automatically 
		self.stockTableView.setShowGrid(False) # remove the grid of the table
		self.stockTableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # remove the scroll bar of the table
		self.stockTableView.setColumnCount(5) # the table has 5 column(name, price, change rate, change, operation)
		self.stockTableView.setHorizontalHeaderLabels(['名称↑↓','现价↑↓','涨跌幅↑↓','涨跌↑↓','操作'])

		# the tail of window (a label)
		self.timeView = QLabel('last update: ',self)
		self.timeView.setGeometry(QRect(0, 270, self.window_width, 20))

		# menu
		self.setContextMenuPolicy(Qt.ActionsContextMenu) # activate menu
		addStockAction = QAction("Add a optional stock", self)
		addStockAction.triggered.connect(self.add_optional_stock_by_name)
		self.addAction(addStockAction)
		quitAction = QAction("Quit", self)
		quitAction.triggered.connect(self.close)
		self.addAction(quitAction)
		self.sort_flag = [False] * 4 # reverse or positive sequence
		self.stockTableView.horizontalHeader().sectionClicked.connect(self.sort_optional_stock)

		self.update_table_view()
		self.update_table_view_data()

		self.show()

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton: # press the left key of mouse
			self._startPos = event.pos() # record the start position of the cursor before moving

	def mouseMoveEvent(self, event):
		self._wmGap = event.pos() - self._startPos # move distance = current position - start position
		final_pos = self.pos() + self._wmGap # the position where the window is currently supposed to be
		
		# The window should not be moved out of the left side of the screen.
		if self.frameGeometry().topLeft().x() + self._wmGap.x() <= 0:
			final_pos.setX(0)
		# The window should not be moved out of the top side of the screen.
		if self.frameGeometry().topLeft().y() + self._wmGap.y() <= 0:
			final_pos.setY(0)
		# The window should not be moved out of the right side of the screen.
		if self.frameGeometry().bottomRight().x() + self._wmGap.x() >= self.screen_width:
			final_pos.setX(self.screen_width - self.window_width)
		# The window should not be moved out of the below side of the screen.
		if self.frameGeometry().bottomRight().y() + self._wmGap.y() >= self.screen_height:
			final_pos.setY(self.screen_height - self.window_height)
		self.move(final_pos) # move window

	def mouseReleaseEvent(self, event):
		# clear _startPos and _wmGap
		if event.button() == Qt.LeftButton:
			self._startPos = None
			self._wmGap = None
		if event.button() == Qt.RightButton:
			self._startPos = None
			self._wmGap = None

	def enterEvent(self, event):
		self.hide_or_show('show', event)

	def leaveEvent(self, event):
		self.hide_or_show('hide', event)

	def hide_or_show(self, mode, event):
		pos = self.frameGeometry().topLeft()
		if mode == 'show' and self.hidden: # try to pop up the window
			# The window is hidden on the right side of the screen
			if pos.x() + self.window_width >= self.screen_width:
				self.startAnimation(self.screen_width - self.window_width, pos.y())
				event.accept()
				self.hidden = False
			# The window is hidden on the left side of the screen
			elif pos.x() <= 0:
				self.startAnimation(0, pos.y())
				event.accept()
				self.hidden = False
			# The window is hidden on the top side of the screen
			elif pos.y() <= 0:
				self.startAnimation(pos.x(), 0)
				event.accept()
				self.hidden = False
		elif mode == 'hide' and (not self.hidden): # try to hide the window
			# The window is on the right side of the screen
			if pos.x() + self.window_width >= self.screen_width:
				self.startAnimation(self.screen_width - 10, pos.y(), mode, 'right')
				event.accept()
				self.hidden = True
			# The window is on the left side of the screen	
			elif pos.x() <= 0:
				self.startAnimation(10 - self.window_width, pos.y(), mode, 'left')
				event.accept()
				self.hidden = True
			# The window is on the top side of the screen
			elif pos.y() <= 0:
				self.startAnimation(pos.x(), 10 - self.window_height, mode, 'up')
				event.accept()
				self.hidden = True

	def startAnimation(self, x, y, mode='show', direction=None):
		animation = QPropertyAnimation(self, b"geometry", self)
		animation.setDuration(200) # the duration of the moving animation
		if mode == 'hide':
			if direction == 'right':
				animation.setEndValue(QRect(x, y, 10, self.window_height))
			elif direction == 'left':
				animation.setEndValue(QRect(0, y, 10, self.window_height))
			else:
				animation.setEndValue(QRect(x, 0, self.window_width, 10))
		else:
			animation.setEndValue(QRect(x, y, self.window_width, self.window_height))
		# start show the animation that the shape of the window becomes the shape of EndValue
		animation.start()

	def add_optional_stock_by_name(self):
		name, ok = QInputDialog.getText(self, 'Stock Name', '输入股票名称')
		if ok:
			res = Fetcher().get_market_and_code(name)	
			if res:
				self.stocks.add_stock(res[0], res[1])
				self.__update_optional_stock()
			else:
				QMessageBox.information(self,'error','搜索不到改股票!',QMessageBox.Ok)

	def closeEvent(self, event):
		self.timer.stop()

	# flush static data
	def update_table_view(self):
		self.stockTableView.clearContents() # clear table
		self.stockTableView.setRowCount(len(self.stockTable))
		# set format and '--' for each unit in table
		for i in range(len(self.stockTable)):
			for j in range(self.stockTableView.columnCount() - 1):
				item = QTableWidgetItem()
				item.setText('--')
				item.setTextAlignment(Qt.AlignVCenter|Qt.AlignHCenter) # alignment
				self.stockTableView.setItem(i, j, item)

				topBtn = QPushButton()
				topBtn.setText('🔝')
				topBtn.setFixedSize(25,25)
				topBtn.clicked.connect(partial(self.top_optional_stock, i))
				delBtn = QPushButton()
				delBtn.setFixedSize(25,25)
				delBtn.setText('×')
				delBtn.clicked.connect(partial(self.del_optional_stock, i))
				lay = QHBoxLayout()
				lay.addWidget(topBtn)
				lay.addWidget(delBtn)
				subWidget = QWidget()
				subWidget.setLayout(lay)
				self.stockTableView.setCellWidget(i, self.stockTableView.columnCount() - 1, subWidget)

	# flush dynamic data
	def update_table_view_data(self):
		lastTime = ''
		for i in range(len(self.stockTable)): # for each every stock
			stock = self.stockTable[i]
			data = {}
			try:
				data = Fetcher().get_quotation(stock['market'], stock['code'])
			except:
				QMessageBox.information(self,'error','不能获取到股票信息!',QMessageBox.Ok)
				self.close()

			# fill dynamic data for items of a stock
			
			self.stockTableView.item(i, 0).setText(data['name'])
			self.stockTableView.item(i, 1).setText(data['price'])
			# stcok_rate return a string of a percentage
			self.stockTableView.item(i, 2).setText(stock_rate( float(data['price']) , float(data['close']) ))
			# set font color according to change of stocks
			if float(data['price']) > float(data['close']):
				self.stockTableView.item(i, 2).setForeground(QBrush(QColor(255,0,0)))
			else:
				self.stockTableView.item(i, 2).setForeground(QBrush(QColor(0,255,0)))

			self.stockTableView.item(i, 3).setText("%.2f" % (float(data['price']) - float(data['close'])))
			# set font color according to change of stocks
			if float(data['price']) > float(data['close']):
				self.stockTableView.item(i, 3).setForeground(QBrush(QColor(255,0,0)))
			else:
				self.stockTableView.item(i, 3).setForeground(QBrush(QColor(0,255,0)))

			# set timestamp string
			lastTime = data['date'] + ' ' + data['time']

		self.timeView.setText('last update: ' + lastTime)

	def __update_optional_stock(self):
		self.timer.stop()
		self.stockTable = self.stocks.stocks
		self.update_table_view()
		self.update_table_view_data()
		self.timer.start(self.tick)

	# index: sort by the index'th column 
	def sort_optional_stock(self, index : int):
		if index == 0:
			for i in range(len(self.stocks.stocks)):
				self.stocks.stocks[i]['key'] = self.stockTableView.item(i, 0).text()
		elif index == 1 or index == 3:
			for i in range(len(self.stocks.stocks)):
				self.stocks.stocks[i]['key'] = float(self.stockTableView.item(i, index).text())
		elif index == 2:
			for i in range(len(self.stocks.stocks)):
				self.stocks.stocks[i]['key'] = float(self.stockTableView.item(i, index).text().strip('%'))
		else:
			raise ValueError('sort_optional_stock index error')
		self.stocks.sort_stock(self.sort_flag[i])
		self.sort_flag[i] = ~self.sort_flag[i] # inverse sort method
		self.__update_optional_stock()

	def top_optional_stock(self, row):
		self.stocks.top_stock(row)
		self.__update_optional_stock()

	def del_optional_stock(self, row):
		self.stocks.del_stock(row)
		self.__update_optional_stock()

if __name__ == '__main__':

	app = QApplication(sys.argv)
	
	screen_width = app.primaryScreen().geometry().width()
	screen_height = app.primaryScreen().geometry().height()

	window = Window(screen_width, screen_height, 800, 300)

	sys.exit(app.exec_())
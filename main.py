from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import csv
import time, math
from decimal import Decimal
from pushsafer import Client


from creds import login_username, login_password, pusher_privatekey

driver = webdriver.Firefox()

def D(num):
	return float(num)

tickerList   = [ 'BRBK',  'CMTE',  'FBLE',  'OZTE',  'ROVR',  'RMFR',  'SMPT',  'SPRK']
tickerOddsV1 = [D(0.30), D(0.65), D(0.40), D(0.35), D(0.70), D(0.65), D(0.70), D(0.45)]	# My value for probability of success
tickerOddsV2 = [D(0.40), D(0.55), D(0.30), D(0.45), D(0.70), D(0.65), D(0.70), D(0.45)]
tickerOddsV3 = [D(0.40), D(0.55), D(0.30), D(0.45), D(0.25), D(0.35), D(0.85), D(0.55)]	# June 16, 2022 (11pm)
tickerOdds   = [D(0.40), D(0.45), D(0.30), D(0.45), D(0.25), D(0.35), D(0.85), D(0.55)]	# June 16, 2022 (1pm)
# buyPriceAt = [D(0.2),  D(0.3)]
# empPriceAt = [D()]
prevBidPrice = [   -1,      -1,      -1,      -1,      -1,      -1,      -1,      -1  ]
prevAskPrice = [  999,     999,     999,     999,     999,     999,     999,     999  ]
currBidPrice = [   -1,      -1,      -1,      -1,      -1,      -1,      -1,      -1  ]
currAskPrice = [  999,     999,     999,     999,     999,     999,     999,     999  ]

def getTransactions():
	driver.get("https://epm.sauder.ubc.ca/default.php?page=history.php")

	time.sleep(2.5) # in seconds
	webElem = driver.find_elements(By.CLASS_NAME, "sortable")
	myTransactions = webElem[0]
	recentOfferTransactions = webElem[1]
	recentBidTransactions = webElem[2]

	marketOfferElemOutput = []
	marketOfferTable = recentOfferTransactions.find_elements(By.TAG_NAME, "tr")
	for row in marketOfferTable:
		cells = row.find_elements(By.TAG_NAME, "td")
		for cell in cells:
			marketOfferElemOutput.append(cell.text)

	marketBidElemOutput = []
	marketBidTable = recentBidTransactions.find_elements(By.TAG_NAME, "tr")
	for row in marketBidTable:
		cells = row.find_elements(By.TAG_NAME, "td")
		for cell in cells:
			marketBidElemOutput.append(cell.text)

	print("Getting transactions information successful")
	return (marketOfferElemOutput, marketBidElemOutput)

def parseTransactions(lst):
	outputTable = []
	for i in range(math.ceil(len(lst)/5)):
		currTuple = (lst[(i*5)], lst[(i*5)+1], int(lst[(i*5)+2]), lst[(i*5)+3], lst[(i*5)+4])
		outputTable.append(currTuple)
	
	return outputTable

def tableToCSV(str):
	if(str=='offers' or str=='bids'):
		cols = ["Symbol", "Shares", "Asking Price/Share", "Post Date"]
		rows = getData(str)
		if(str=='offers'):
			offerData = rows
		else:
			bidData = rows

		with open('./output/' + str + '.csv', 'w') as f:
			write = csv.writer(f)
			write.writerow(cols)
			write.writerows(rows)

	elif(str=='history'):
		cols = ["Date", "Stock", "Shares Bought", "$/Share", "Total"]
		transactions = getTransactions()
		rowsOffers = parseTransactions(transactions[0])
		rowsBids = parseTransactions(transactions[1])

		with open('./output/offerTransactions.csv', 'w') as f:
			write = csv.writer(f)
			write.writerow(cols)
			write.writerows(rowsOffers)

		with open('./output/bidTransactions.csv', 'w') as f:
			write = csv.writer(f)
			write.writerow(cols)
			write.writerows(rowsBids)
	
	else:
		raise Exception("Non Valid String")

def parseTable(table):
	outputTable = []

	for i in range(math.ceil(len(table)/4)):
		currTuple = (table[(i*4)], int(table[(i*4)+1]), table[(i*4)+2], table[(i*4)+3])
		outputTable.append(currTuple)
	
	return outputTable

def getData(str):
	if(not(str=='offers' or str=='bids')):
		raise Exception("Non Valid String")
	
	driver.get("https://epm.sauder.ubc.ca/default.php?page=" + str + ".php")

	time.sleep(2.5) # in seconds
	webElem = driver.find_elements(By.CLASS_NAME, "sortable")
	marketElem = webElem[0]
	offerElem = webElem[1]

	marketElemOutput = []
    
	marketTable = marketElem.find_elements(By.TAG_NAME, "tr")
	for row in marketTable:
		cells = row.find_elements(By.TAG_NAME, "td")
		for cell in cells:
			marketElemOutput.append(cell.text)

	# marketElem.find_element()
	print("Getting " + str + " information successful")
	return parseTable(marketElemOutput)

def login():
	driver.get("https://epm.sauder.ubc.ca/default.php")
	assert "CRABE" in driver.title
	driver.find_element(By.NAME, 'name').send_keys(login_username)
	driver.find_element(By.NAME, 'password').send_keys(login_password)
	driver.find_element(By.CSS_SELECTOR, 'input[type="submit" i]').click()

	print("Login Successful")

def getCSVData():
	tableToCSV('offers')
	tableToCSV('bids')
	tableToCSV('history')

# Find index in relation to ticker
def tickerToIndex(tkr):
	match tkr:
		case 'BRBK':
			return 0
		case 'CMTE':
			return 1
		case 'FBLE':
			return 2
		case 'OZTE':
			return 3
		case 'ROVR':
			return 4
		case 'RMFR':
			return 5
		case 'SMPT':
			return 6
		case 'SPRK':
			return 7

def indexToTicker(idx):
	match idx:
		case 0:
			return 'BRBK'
		case 1:
			return 'CMTE'
		case 2:
			return 'FBLE'
		case 3:
			return 'OZTE'
		case 4:
			return 'ROVR'
		case 5:
			return 'RMFR'
		case 6:
			return 'SMPT'
		case 7:
			return 'SPRK'

# Get rid of dollar sign and return value as Decimal
def decimaler(str):
	return Decimal(str[1:])

def initTickerTable(n):
	table = []
	for t in tickerList:
		curr = []
		curr.append(t)
		for _ in range(n):
			curr.append(0)
		table.append(curr)
	return table


def normalizeOutput(str):
	tickerNormalized = initTickerTable(3) # Total Shares, Market Cap, Avg. Price/Share
	
	with open('./output/' + str + '.csv', 'r') as f:
		reader = csv.reader(f, delimiter=",")
		for i, line in enumerate(reader):
			if(i == 0):
				continue

			symbol = line[0]
			index = tickerToIndex(symbol)
			tickerNormalized[index][1] += int(line[1])
			tickerNormalized[index][2] += (Decimal(int(line[1])) * decimaler(line[2]))

	for i in range(len(tickerList)):
		if tickerNormalized[i][1] == 0:
			tickerNormalized[i][3] = 0
		else:
			tickerNormalized[i][3] = Decimal(tickerNormalized[i][2] / tickerNormalized[i][1])

	return tickerNormalized
	
def normToCSV(str):
	cols = ["Symbol", "Total Shares", "Market Cap", "Avg. Price/Share"]
	rows = normalizeOutput(str)

	with open('./output/' + str + 'Normalized.csv', 'w') as f:
		write = csv.writer(f)
		write.writerow(cols)
		write.writerows(rows)

def normalizeData():
	normToCSV('bids')
	normToCSV('offers')
	# normalizeOutputTransactions('bids')
	# normalizeOutputTransactions('offers')

def getPrice(str, fileExtension=''):
	tickerPrice = []
	for t in tickerList:
		curr = []
		curr.append(t)
		if(str == 'offers'):
			curr.append(Decimal(9999999))
		else:
			curr.append(Decimal(0))
		curr.append(0)
		tickerPrice.append(curr)

	with open('./output/' + str + '.csv', 'r') as f:
		reader = csv.reader(f, delimiter=",")
		for i, line in enumerate(reader):
			if(i == 0):
				continue

			symbol = line[0]
			index = tickerToIndex(symbol)
			ppp = decimaler(line[2])	# price per share
			if(str == 'bids'):
				if(tickerPrice[index][1] < ppp):
					tickerPrice[index][1] = ppp
					tickerPrice[index][2] = int(line[1])
				elif(tickerPrice[index][1] == ppp):
					tickerPrice[index][2] += int(line[1])
			else:
				if(tickerPrice[index][1] > ppp):
					tickerPrice[index][1] = ppp
					tickerPrice[index][2] = int(line[1])
				elif(tickerPrice[index][1] == ppp):
					tickerPrice[index][2] += int(line[1])

	if(str == 'bids'):
		cols = ["Symbol", "Max Bid", "Amount"]
	else:
		cols = ["Symbol", "Min Ask", "Amount"]
	
	rows = tickerPrice

	with open('./output/' + str + fileExtension + 'Price.csv', 'w') as f:
		write = csv.writer(f)
		write.writerow(cols)
		write.writerows(rows)


def calculatePrice():
	tickerPrice = initTickerTable(8)

	strList = ['bids', 'offers']
	bidCap = [0, 0, 0, 0, 0, 0, 0, 0]
	bidShare = [0, 0, 0, 0, 0, 0, 0, 0]
	askCap = [0, 0, 0, 0, 0, 0, 0, 0]
	askShare = [0, 0, 0, 0, 0, 0, 0, 0]

	for type in strList:
		with open('./output/' + type + 'Price.csv', 'r') as f:
			reader = csv.reader(f, delimiter=",")
			
			for i, line in enumerate(reader):
				if(i == 0):
					continue

				if(type == 'bids'):
					tickerPrice[i-1][1] = line[1]
				else:
					tickerPrice[i-1][2] = line[1]

		with open('./output/' + type + 'Normalized.csv', 'r') as f:
			reader = csv.reader(f, delimiter=",")
			
			for i, line in enumerate(reader):
				if(i == 0):
					continue

				if(type == 'bids'):
					bidCap[i-1] = line[2]
					bidShare[i-1] = line[1]
					tickerPrice[i-1][4] = line[3]
				else:
					askCap[i-1] = line[2]
					askShare[i-1] = line[1]
					tickerPrice[i-1][5] = line[3]
	
	cols = ['Symbol', 'Max Bid', 'Min Ask', 'Min/Max Spread', 'Avg Bid', 'Avg Ask', 'Avg Price', 'AvgSpread', 'My Odds']

	for i in range(len(tickerPrice)):
		# print(i)
		# print(tickerPrice)
		tickerPrice[i][3] = (Decimal(tickerPrice[i][2]) - Decimal(tickerPrice[i][1]))/Decimal(tickerPrice[i][2])
		avgDifference = Decimal(tickerPrice[i][5]) - Decimal(tickerPrice[i][4])
		# TODO: Better avg pricing calculation
		tickerPrice[i][6] = Decimal(tickerPrice[i][4])+(avgDifference*Decimal(int(bidShare[i])/(int(bidShare[i])+int(askShare[i]))))
		if(Decimal(tickerPrice[i][5]) == 0):
			tickerPrice[i][7] = 0
		else:
			tickerPrice[i][7] = avgDifference/Decimal(tickerPrice[i][5])
		tickerPrice[i][8] = tickerOdds[i]
		rows = tickerPrice

	with open('./output/calculatedPrices.csv', 'w') as f:
		write = csv.writer(f)
		write.writerow(cols)
		write.writerows(rows)


def getPrices():
	getPrice('bids')
	getPrice('offers')
	calculatePrice()

def update():
	getCSVData()
	normalizeData()
	getPrices()
	
def getMinAskPrevPrices(table):
	for transaction in table:
		if(decimaler(transaction[2])<prevAskPrice[tickerToIndex(transaction[0])]):
			prevAskPrice[tickerToIndex(transaction[0])] = decimaler(transaction[2])

def getMaxBidPrevPrices(table):
	for transaction in table:
		if(decimaler(transaction[2])>prevBidPrice[tickerToIndex(transaction[0])]):
			prevBidPrice[tickerToIndex(transaction[0])] = decimaler(transaction[2])

def getMinAskCurrPrices(table):
	for transaction in table:
		if(decimaler(transaction[2])<currAskPrice[tickerToIndex(transaction[0])]):
			currAskPrice[tickerToIndex(transaction[0])] = decimaler(transaction[2])

def getMaxBidCurrPrices(table):
	for transaction in table:
		if(decimaler(transaction[2])>currBidPrice[tickerToIndex(transaction[0])]):
			currBidPrice[tickerToIndex(transaction[0])] = decimaler(transaction[2])

def writeToPrev():
	getMinAskPrevPrices(getData('offers'))
	getMaxBidPrevPrices(getData('bids'))

def writeToCurr():
	getMinAskCurrPrices(getData('offers'))
	getMaxBidCurrPrices(getData('bids'))

def check():
	global prevAskPrice, currAskPrice, prevBidPrice, currBidPrice
	writeToCurr()
	if(prevAskPrice != currAskPrice):
		print("ASK CHANGE")
		for i in range(len(tickerList)):
			if(prevAskPrice[i] != currAskPrice[i]):
				autoMessage(indexToTicker(i), 'Ask', prevAskPrice[i], currAskPrice[i])
		prevAskPrice = currAskPrice

	if(prevBidPrice != currBidPrice):
		print("BID CHANGE")
		for i in range(len(tickerList)):
			if(prevBidPrice[i] != currBidPrice[i]):
				autoMessage(indexToTicker(i), 'Bid', prevBidPrice[i], currBidPrice[i])
		prevBidPrice = currBidPrice

def autoMessage(ticker, type, prevAmount, currAmount):
	sendNotification(type + ' ' + ticker + ' price Δ', str(prevAmount) + ' -> ' + str(currAmount))

def sendNotification(title, body):
	client = Client(pusher_privatekey)
	resp = client.send_message(body, title, "54342", "1", "4", "2", "https://www.pushsafer.com", "Open Pushsafer", "0", "2", "60", "600", "1", "", "", "")
	print(resp)


def main():
	login()
	update()
	writeToPrev()
	while(True):
		time.sleep(10) # seconds to wait before updating
		check()

if __name__ == '__main__':
	main()

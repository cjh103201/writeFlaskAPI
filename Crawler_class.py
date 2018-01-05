import sys
import time
import random
from selenium import webdriver
from bs4 import BeautifulSoup

class DaumDictCrawler:
	def __init__(self):
		self.drvr = webdriver.Chrome("./chromedriver")
		self.hashTable = {}

	def performSentenceDB(self, levelDepth, seed, maxSentPerWord, seedPerSet = 0):
		# 다음 사전 api가 있을 경우 검색을 하고 결과가 같으면 제외하는 구문이 필요하다.
		searchStack = []
		sent_set = []
		searchStack.append(seed)
		for i in range(levelDepth):
			tempStack = []
			while True:
				seed = searchStack.pop()
				url = "http://dic.daum.net/search.do?q="+seed+"&dic=kor"
				try:
					self.drvr.get(url)
				except:
					searchStack.append(seed)
					time.sleep(0.2)
					continue
				sent_set += self.exampleSentenceOfWord(seed, maxSentPerWord)
				tempStack += self.stackSearchWord(sent_set, seedPerSet)
				# print(sent) ##### mysql로 보내는 부분집어넣을것 sent_set 초기화는 for 문 안으로 집어넣고 
				if len(searchStack) == 0:
					if i == levelDepth - 1:
						break
					else:
						searchStack = tempStack
						break
		self.drvr.quit()
		return sent_set

	def exampleSentenceOfWord(self, seed, maxSentPerWord):
		sent_set = []
		try:
			element = self.drvr.find_element_by_class_name('list_example')
		except:
			print("There is no example of the word:", seed)
		try:
			element = self.drvr.find_element_by_xpath('//div[@class="cont_example"]/a')
		except:
			pass # Less than 5 sentences
		for i in range(int(maxSentPerWord/5)-1):
			try:
				time.sleep(0.1)
				element.click()
			except:
				print(sys.exc_info()[0])
				break
		html_source = self.drvr.page_source
		self.soup = BeautifulSoup(html_source,'lxml')
		example_set = self.soup.find_all('span', class_='txt_example')
		for example in example_set:
			example = example.get_text()
			example = self.daumExampleSentCleaning(example)
			if self.checkDuplicate(example) == True:
				continue
			example = self.filterNotAllowedAlph(example)
			sent_set.append(example)
		return sent_set

	def stackSearchWord(self, sent_set, seedPerSet):
		returnList = []
		for sent in sent_set:
			children = sent.split()
			for word in children:				
				if len(word) >= 2 and not self.checkDuplicate(word):
					returnList.append(word)
		if seedPerSet == 0:
			return returnList
		else:
			returnList = self.reservoirSampling(returnList, seedPerSet)
			return returnList
		#[child.string for child in self.soup.find_all('span', class_ = 'txt_ex')[0].children if len(child.string) >= 2 and not checkDuplicate(child.string)]

	def daumExampleSentCleaning(self, sent):
		cnt = 0
		alph = ''
		while alph != '(':
			cnt +=1
			alph = sent[-cnt]
		sent = sent[:-cnt]
		sent = sent.rstrip()
		return sent

	def allowedUniCheck(self, alph):
		temp = ord(alph)
		#allowed = [A-zㄱ-ㅎㅏ-ㅢ가-힣',','.',' ']
		if temp >= 44032 and temp <= 55203:
			return True
		elif temp == 32:
			return True
		elif temp >= 65 and temp <= 122:
			return True
		elif temp >= 48 and temp <= 57:
			return True
		elif temp >= 12593 and temp <= 12643:
			return True
		elif temp == 46 or temp == 44:
			return True
		else:
			return False

	def filterNotAllowedAlph(self, sent):
		new = ''
		for alph in sent:
			if self.allowedUniCheck(alph) == True:
				new += alph
		return new

	def checkDuplicate(self, string):
		try:
			self.hashTable[string]
			return True
		except:
			self.hashTable[string] = True
			return False
		#체크하고 차있으면 return True 만약 비어있을 시에 md5 insert를 진행하고 false를 돌려줌

	def reservoirSampling(self, items, k):
		if len(items) <= k:
			return items
		sample = items[0:k]
		for i in range(k, len(items)):
			j = random.randrange(1, i + 1)
			if j <= k:
				sample[j-1] = items[i]
		return sample

if __name__ == '__main__':
	daumDict = DaumDictCrawler()
	sent_set = daumDict.performSentenceDB(2, '여행', 10, 10)
	print("#"*70)
	for i in sent_set:
		print(i)
	print("#"*70)
	print("Num of sentences:", len(sent_set))
	print("Num of duplicated sentences:", len(sent_set)-len(set(sent_set))) # 이거 0이어야
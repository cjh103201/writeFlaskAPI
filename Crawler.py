import Crawler_class
import pymysql

seed_set = ['같이', '안녕하세요', '나는', '오늘', '했어요', '치킨', '게임', '고향', '집', '어릴', '김치', '국밥', '처음']
with pymysql.connect(host='localhost', user='root', 
					passwd='', db='daum_dict_sentences', charset='utf8') as conn:
	query = 'insert ignore into sentences (sentence, md5_hash) values (%s , MD5(%s))'
	for seed in seed_set:
		crawler = Crawler_class.DaumDictCrawler()
		sent_set = crawler.performSentenceDB(2, seed, 500, 50)
		for sent in sent_set:
			conn.execute(query, (sent, sent))
			
#passwd = xxxxxxxqwe
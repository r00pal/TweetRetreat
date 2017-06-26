import MySQLdb 
import datetime

HOST = ""
USER = ""
PASSWD = ""
DATABASE = ""

def fetch_query(tweet_id):
    db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "SELECT * from tweet_info where tweet_id = {}; ".format(tweet_id)
    cursor.execute(query)
    data_main = cursor.fetchone()
    query = "SELECT * from tweet_info where parent_id = {}; ".format(tweet_id)
    cursor.execute(query)

    data = cursor.fetchall()
    data = list(data)
    data.append(data_main)
   

    cursor.close()
    db.close()

    return data

if __name__ == '__main__':
    data = fetch_query(875558348506189824)
    print (data)

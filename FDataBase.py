import sqlite3
import time
import math, os
from datetime import datetime
import shutil
import random


class FDataBase:
    

    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getPost(self, url):
        try:
            self.__cur.execute(f"SELECT title, content, date, visits FROM blog WHERE url LIKE '{url}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Error gettin post from db "+str(e))
 
        return (False, False, False)
    
    def getShawsData(self):
        sql = '''SELECT rowid, * FROM shawarma ORDER BY rating'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Error reading DB")
        return []

    def getCatData(self):
        sql = '''SELECT rowid, * FROM cat ORDER BY rowid DESC'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Error reading DB")
        return []
    
    def getBooksData(self):
        sql = '''SELECT rowid, * FROM books'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Error reading DB")
        return []



    def getBlogData(self, search, sort):
        if search != '' and sort == 'Новые':
            sql = f"SELECT rowid, * FROM blog WHERE title LIKE '%{search.lower()}%' ORDER BY rowid DESC"
        elif search != '' and sort == 'Старые':
            sql = f"SELECT rowid, * FROM blog WHERE title LIKE '%{search.lower()}%' ORDER BY rowid ASC"
        if search != '' and sort == 'Популярные':
            sql = f"SELECT rowid, * FROM blog WHERE title LIKE '%{search.lower()}%' ORDER BY visits DESC"
        elif search != '' and sort == 'Непопулярные':
            sql = f"SELECT rowid, * FROM blog WHERE title LIKE '%{search.lower()}%' ORDER BY visits ASC"

        elif search == '' and sort == 'Новые':
            sql = f"SELECT rowid, * FROM blog ORDER BY rowid DESC"
        elif search == '' and sort == 'Старые':
            sql = f"SELECT rowid, * FROM blog ORDER BY rowid ASC"
        if search == '' and sort == 'Популярные':
            sql = f"SELECT rowid, * FROM blog ORDER BY visits DESC"
        elif search == '' and sort == 'Непопулярные':
            sql = f"SELECT rowid, * FROM blog ORDER BY visits ASC"

        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Error reading DB")
        return []

    def getMySitesData(self):
        sql = '''SELECT rowid, * FROM links'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Error reading DB")
        return []

    def getComments(self, url):
        sql = f"SELECT rowid, * FROM comments WHERE url LIKE '{url}'"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Error reading DB")
        return []

    def getURL(self, id):
        sql = f"SELECT url FROM comments WHERE rowid = {id}"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res[0]['url']
        except:
            print("Error reading DB")
        return []
    
    def addPost(self, title, url, content):
        try:
            date = str(datetime.now() .strftime("%d.%m.%Y"))
            visits = 0
            self.__cur.execute(f"INSERT INTO blog VALUES('{url}', '{content}', {visits}, '{title.lower()}', '{date}')")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while adding "+str(e))
            return False
        return True


    def addComment(self, comment, admin, reply, url):
        adj = [
            "милейший",
            "зоркий",
            "дьявольский",
            "банановый",
            "добрый",
            "злой",
            "соседский",
            "ржавый",
            "мокрый",
            "кривой",
            "старый",
            "хипстерский",
            "настоящий",
            "летающий",
            "тёмный"
            ]
        noun = [
            'огородник', 
            "сверчок", 
            "дьявол", 
            "пакет", 
            "десерт", 
            "тапок", 
            "кот", 
            "инженер", 
            "полковник", 
            "гвоздодёр", 
            "косинус",
            "моряк",
            "куст",
            "подстрекатель",
            "плинтус"]
        try:
            if admin:
                name = "САМЫЙ ГЛАВНЫЙ"
                avatar = 0
            else:
                name = random.choice(adj).upper() + ' ' + random.choice(noun).upper()
                avatar = random.randint(1, 9)
            
            self.__cur.execute(f"INSERT INTO comments VALUES('{name}', '{comment}', '{reply}', {avatar}, '{url}')")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while adding "+str(e))
            return False

    def addBook(self, author, title, file):
        try:
            self.__cur.execute(f"INSERT INTO books VALUES('{author}', '{title}', '{file}')")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while adding "+str(e))
            return False
        return True

    


    def addCatPhoto(self, description, file):
        try:
            tm = math.floor(time.time())
            self.__cur.execute(f"INSERT INTO cat VALUES('{description}', '{file}')")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while adding "+str(e))
            return False
        return True

    def addShawarma(self, name, place, mark, rating, link):
        try:
            self.__cur.execute(f"UPDATE shawarma SET rating = rating + 1 WHERE rating >= {rating}")
            self.__db.commit()
            self.__cur.execute(f"INSERT INTO shawarma VALUES({rating}, '{name}', '{place}', {mark}, '{link}')")
            self.__db.commit()
            print("I did")
        except sqlite3.Error as e:
            print("Error while adding "+str(e))
            return False
        return True

    def addSite(self, description, link):
        try:
            self.__cur.execute(f"INSERT INTO links VALUES('{description}', 'http://{link}')")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while adding "+str(e))
            return False
        return True

    def addVisit(self, url):
        try:
            self.__cur.execute(f"UPDATE blog SET visits = visits + 1 WHERE url LIKE '{url}'")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while updating db "+str(e))
            return False
        return True




    def deletePost(self, id):
        try:
            self.__cur.execute(f"SELECT rowid, * FROM blog WHERE rowid = {id}")
            self.__db.commit()
            res = self.__cur.fetchall()[0]['url']
            if os.path.exists('static/files/posts_res/' + res):
                shutil.rmtree('static/files/posts_res/' + res)
            self.__cur.execute(f"DELETE FROM comments WHERE url = '{res}'")
            self.__cur.execute(f"DELETE FROM blog WHERE rowid = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True

    def deleteBook(self, id):
        try:
            self.__cur.execute(f"SELECT rowid, * FROM books WHERE rowid = {id}")
            self.__db.commit()
            res = self.__cur.fetchall()[0]['file']
            if os.path.exists(res):
                os.remove(res)
            self.__cur.execute(f"DELETE FROM books WHERE rowid = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True

    def deleteCatPhoto(self, id):
        try:
            self.__cur.execute(f"SELECT rowid, * FROM cat WHERE rowid = {id}")
            self.__db.commit()
            res = self.__cur.fetchall()[0]['url']
            if os.path.exists(res):
                os.remove(res)
            self.__cur.execute(f"DELETE FROM cat WHERE rowid = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True

    def deleteShawarma(self, id):
        try:
            self.__cur.execute(f"SELECT rowid, * FROM shawarma WHERE rowid = {id}")
            self.__db.commit()
            res = self.__cur.fetchall()[0]['rating']
            self.__cur.execute(f"UPDATE shawarma SET rating = rating - 1 WHERE rating >= {res}")
            self.__db.commit()
            self.__cur.execute(f"DELETE FROM shawarma WHERE rowid = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True

    def deleteSite(self, id):
        try:
            self.__cur.execute(f"DELETE FROM links WHERE rowid = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True

    def deleteComment(self, id):
        try:
            self.__cur.execute(f"DELETE FROM comments WHERE rowid = {id}")
            self.__cur.execute(f"DELETE FROM comments WHERE reply = {id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True

    def getPassword(self):
        try:
            self.__cur.execute(f"SELECT * FROM admin")
            res = self.__cur.fetchall()
            if res: return res[0]['password']
        except sqlite3.Error as e:
            print("Error while deleting "+str(e))
            return False
        return True




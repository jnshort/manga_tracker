from db import db 
import requests
import webbrowser
import bs4 as bs
from pymongo import MongoClient
from tracked import url_list
from validators import *
from constraints import *

base_url = 'https://ww7.mangakakalot.tv'

def create():
    db.drop_database("MangaCollection")
    db.MangaCollection.create_collection("manga", **manga_validator)
    for constraint in manga_constraints:
        db.MangaCollection.manga.create_index(constraint, unique=True)


class Manga:

    def __init__(self, source):
        temp_dict = dict()
        temp_url = ""
        temp_name = ""
        temp_chapter = 0
        temp_chap_list = []
        if type(source) == type(""):
            temp_url = source
            temp_name = self.get_name(source)
            temp_chapter = 1
            temp_chap_list = []
        elif type(dict()) == type(source):
            temp_url = source['url']
            temp_name = source['name']
            temp_chapter = source['current_chapter']
            temp_chap_list = []
            for chapter in source['chapters']:
                temp_chap_list.append(self.Chapter(self, chapter))
        else:
                raise ValueError()
        self.url = temp_url
        self.name = temp_name
        self.current_chapter = temp_chapter
        self.chapters_objs = temp_chap_list

    def __eq__(self, other):
        return self.name == other.name

    def query(self):
        return {'name': self.name}

    def get_name(self, url):
        html = requests.get(url).text
        soup = bs.BeautifulSoup(html, features="html.parser")
        title = ""
        for link in soup.findAll('h1'):
            title = link.text
        return title

    def inc_current_chapter(self):
        self.current_chapter += 1
        

    def get_next_chapter(self):
        return len(self.chapters_objs)+1

    def dict_rep(self):
        chapters_dict = []
        for chap in self.chapters_objs:
            chapters_dict.append(chap.dict_rep())
        return {'name': self.name, 'url': self.url, 'current_chapter': self.current_chapter, 'chapters': chapters_dict}

    def load_chapters(self):
        html = requests.get(self.url).text
        parsed = bs.BeautifulSoup(html, features="html.parser")
        url_list = []
        for chap in parsed.findAll('a'):
            if chap.get('href'):
                if chap.get('href').startswith('/chapter'):
                    temp = base_url + chap.get('href')            
                    url_list.append(temp)
        url_list.reverse()
        for url in url_list:
            ch = self.Chapter(self, url)
            self.chapters_objs.append(ch)

    def set_current(self, chap):
        self.current_chapter = chap

    def insert(self):
        if db.MangaCollection.manga.count_documents(self.query()) == 0:
            db.MangaCollection.manga.insert_one(self.dict_rep())
        else:
            self.update()

    def update(self):
        db.MangaCollection.manga.update_one(self.query(), { '$set': self.dict_rep()})

    class Chapter:

        def __init__(self, manga, source):
            self.manga = manga
            temp_url = ""
            temp_chapter_num = 0
            if type("") == type(source):
                temp_url = source
                temp_chapter_num = self.manga.get_next_chapter()
            elif type(source) == type(dict()):
                    temp_url = source['url']
                    temp_chapter_num = source['chapter_number']
            else:
                raise ValueError()
            self.chapter_num = temp_chapter_num
            self.url = temp_url

        def dict_rep(self):
            return {'name': self.manga.name, 'url': self.url, 
                    'chapter_number': self.chapter_num}
       
def get_tracked_obj():
    tracked_manga_objects = []
    for link in url_list:
        tracked_manga_objects.append(Manga(link))
    return tracked_manga_objects

def get_stored_obj():
    manga_collection = db.MangaCollection.manga.find()
    stored_manga_objects = []
    for doc in manga_collection:
        stored_manga_objects.append(Manga(doc))
    return stored_manga_objects


def startup():
    manga_collection = db.MangaCollection.manga.find()

    tracked_manga_objects = get_tracked_obj()
    stored_manga_objects = get_stored_obj()

    new_manga = len(stored_manga_objects) < len(tracked_manga_objects)

    while new_manga:
        for book in tracked_manga_objects:
            if db.MangaCollection.manga.count_documents(book.query()) == 0:
                book.insert()
        tracked_manga_objects = get_tracked_obj()
        stored_manga_objects = get_stored_obj()
        new_manga = len(stored_manga_objects) < len(tracked_manga_objects)

    for tracked_manga in tracked_manga_objects:
        tracked_manga.load_chapters()


    
    for stored_manga in stored_manga_objects:
        for tracked_manga in tracked_manga_objects:
            if tracked_manga == stored_manga and len(tracked_manga.chapters_objs) > len(stored_manga.chapters_objs):
                stored_manga.chapters_objs = tracked_manga.chapters_objs
        stored_manga.insert()
 
def manga_menu(manga):
    print(f"Selected Manga: {manga.name}")
    choice = 0
    reading = True
    while reading:
        prompt = f"1) read next unread: chapter {manga.current_chapter}\n2) update next chapter \n3) Exit\nEnter choice ---> "
        while choice not in range(1, 4):
            choice = int(input(prompt))
        match choice:
            case 1:
                webbrowser.open_new(manga.chapters_objs[manga.current_chapter-1].url)
                manga.current_chapter += 1
                choice = 0
            case 2:
                max = len(manga.chapters_objs)
                print(f"The most recent is chapter {max}")
                chap = input("Enter next chapter to read ---> ")
                while int(chap) not in range(1,max+1):
                    chap = input("Enter next chapter to read ---> ")
                manga.set_current(int(chap))
                choice = 0
            case 3:
                reading = False
    manga.insert()



def main():
    startup()
    print('Database Updated')
    manga_local = []

    for book in db.MangaCollection.manga.find():
        manga_local.append(Manga(book))

    print('Manga List Loaded')
    print()

    reading = True

    while reading:
        count = 0
        print('What Manga would you like to select?')
        for manga in manga_local:
            count += 1
            print(f"{count}) {manga.name}")
        choice = input("Enter choice ---> ")
        if not choice.isalnum() or int(choice) not in range(1, count+1):
                choice = input("Enter choice ---> ")
        manga_menu(manga_local[int(choice)-1])
        print()
        choice = input("Would you like to keep reading?(Y/N)")
        while choice.upper() not in ['Y', 'N']:
            choice = input("Would you like to keep reading(Y?N)")
        match choice.upper():
            case 'Y':
                reading = True
                print()
            case 'N':
                reading = False


main()

import urllib.request
import re
import urllib.request
import matplotlib.pyplot as plt
from urllib.request import urlopen
from bs4 import BeautifulSoup


# ------------- Question 1 -----------------

def print_table(data, header):
    print("{:<40} {:<8} {:<30} {:<40}".format(header[0][:-1], header[1][:-1], header[2][:-1], header[3][:-1]))
    print('')
    for row in data:
        l = []
        for r in row[0:4]:
            if '\n' in r:
                r = r[:-1]
            l.append(r)
        print("{:<40} {:<8} {:<30} {:<40}".format(l[0], l[1], l[2], l[3]))


URL = 'https://en.wikipedia.org/wiki/Julia_Roberts_filmography'
html = ''

with urllib.request.urlopen(URL) as response:
    html = response.read()

data = []

soup = BeautifulSoup(html, "html.parser")

# find right table in page
table = soup.find('table', attrs={'class': 'wikitable plainrowheaders sortable'})
rows = table.findAll('tr')
info = []
header = []

for th in rows[0].findAll("th"):
    header.append(th.findNext(text=True))

# get movies info
for tr in rows[1:]:
    row = []
    row.append(tr.find("th").findNext(text=True))
    for td in tr.findAll("td"):
        row.append(td.findNext(text=True))
    info.append(row)

print('------------- Question 1 ---------------')
print()
print_table(info, header)


# ------------- Question 2 -----------------

def printTable(data):
    print("{:<4} {:<40} {:<15} {:<30} {:<3}".format('#','Name', 'Year of birth', 'Country of birth', 'Awards'))
    print('')
    i = 1
    for row in data:
        print("{:<4} {:<30} {:<15} {:<30} {:<3}".format(i, row[0], row[1], row[2], row[3]))
        i += 1


# returns a list of all the co-actors' page links
def getCoActor(html):
    wikiUrl='https://en.wikipedia.org'
    url = 'https://en.wikipedia.org'+html
    curr_movie_html=''
    with urllib.request.urlopen('https://en.wikipedia.org'+html) as response:
        curr_movie_html = response.read()
    curr_movie_html = BeautifulSoup(curr_movie_html, "html.parser") #"html.parser"
    header = curr_movie_html.find("span", class_="mw-headline", text=re.compile('(Cast)|(cast)'))
    actors_hyperLinks = []
    if header:
        parent = header.parent
        cast_data = parent.findNext(["ul", "table"])
        if cast_data.name == 'ul':
            for li in cast_data.findAll('li'):
                link = li.find('a')
                name = li.find(text=True)
                if not re.match("Julia Roberts", name) and link:
                    link = 'https://en.wikipedia.org'+link.get("href")
                    actors_hyperLinks.append(link)
        else:
            rows = cast_data.findAll('tr')
            for tr in rows[1:]:
                cell = tr.find("td")
                link = cell.find('a', href=True)
                name = cell.find(text=True)
                if not re.match("Julia Roberts", name) and link:
                    actors_hyperLinks.append(wikiUrl+link['href'])
    return actors_hyperLinks


URL = 'https://en.wikipedia.org/wiki/Julia_Roberts_filmography'
html = ''
with urllib.request.urlopen(URL) as response:
    html = response.read()

soup = BeautifulSoup(html, "html.parser")
table = soup.find('table', attrs={'class':'wikitable plainrowheaders sortable'})
rows = table.findAll('tr')
movies_hyperLinks = []
actors_links = []
for tr in rows[1:]:
    for th in tr.findAll('th'):
        link = th.findAll("a")
        if len(link) > 0:
            movies_hyperLinks.append(link[0].get("href"))
for movie in movies_hyperLinks:
    arr = getCoActor(movie)
    for x in arr:
        actors_links.append(x)

# collect info about each co-actor
info = []
for actor in actors_links:
    try:
        asoup = BeautifulSoup(urlopen(actor), "html.parser")
    except:
        continue

    name = asoup.find("h1", class_= "firstHeading").find(text=True)
    try:
        box = asoup.find("table", class_ = re.compile('infobox')).find("th",text = re.compile('Born')).parent
        try:
            bornYear = box.find("span",class_="bday").find(text=True)
        except:
            bornYear = '-'
        try:
            country = box.find("div",class_= "birthplace").findAll(text= True)[-1].replace(',','')
        except:
            country = '-'
    except:
        bornYear = '-'
        country = '-'

    awards = "https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_" + name.replace(' ', '_')
    try:
        aw_soup = BeautifulSoup(urlopen(awards), "html.parser")
        nawards = len(aw_soup.findAll("td", class_ = "yes table-yes2", text = re.compile('Won')))
    except:
        nawards = 0

    info.append([name, bornYear, country, nawards])

print('------------- Question 2 ---------------')
print()
printTable(info)


# ------------- Question 3 -----------------

names_list = []
for row in info:
    names_list.append(row[0])

names_list.sort()

joint_movies = []

# count duplicates
curr = names_list[0]
count = 1
for a in names_list[1:]:
    if a == curr:
        count = count + 1
    else:
        joint_movies.append([curr, count])
        count = 1
        curr = a
joint_movies.append([curr, count])

print('------------- Question 3 ---------------')
print()
# print table
print("{:<4} {:<40} {:<15}".format('#', 'Name', 'Num of joint movies'))
print('')
i = 1
for r in joint_movies:
    print("{:<4} {:<40} {:<15}".format(i, r[0], r[1]))
    i += 1


joint_movies_num = []

# get only the number of joint movies, without the co-actors names
for m in joint_movies:
    joint_movies_num.append(m[1])

max_movies = max(joint_movies_num)

# the indexes of the list represent the number of joint movies, and the content represent the number of co-actors
actors_num = [0] * (max_movies + 1)

for n in joint_movies_num:
    actors_num[n] = actors_num[n] + 1

xAxis = []
yAxis = []
j = 0
for e in actors_num:
    if e > 0:
        xAxis.append(j)
        yAxis.append(e)
    j += 1

plt.hist(joint_movies_num, bins=xAxis)

plt.ylabel("Num of actors")
plt.xlabel("Num of joint movies")

plt.show()

from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")

    #Find the key to get the information
    movie_list = soup.find('div', attrs={'class':'lister-list'})
    movie_list_array = movie_list.findAll('div', attrs={'class':'lister-item-content'})

    temp = [] #initiating a tuple

    for i in range(0, len(movie_list_array)):
        #use the key to take information here
        movie = movie_list_array[i]

        judul = movie.find('h3', attrs={'class':'lister-item-header'}).find('a').text.strip()
        imdb_rating = movie.find('div',attrs={'class':'inline-block ratings-imdb-rating'}).find('strong').text.strip()
        if movie.find('div',attrs={'class':'inline-block ratings-metascore'}) is None:
            metascore = 0
        else:
            metascore = movie.find('div',attrs={'class':'inline-block ratings-metascore'}).find('span').text.strip()
        votes = movie.find('span',attrs={'name':'nv'}).text.strip()
        temp.append((judul, imdb_rating, metascore, votes)) #append the needed information 

    temp = temp[::-1]

    df = pd.DataFrame(temp, columns = ('judul','imdb_rating', 'metascore','votes')) #creating the dataframe

    #data wranggling -  try to change the data type to right data type
    df['judul'] = df['judul'].astype('category')
    df['imdb_rating'] = df['imdb_rating'].astype('float64')
    df['votes'] = df['votes'].str.replace(",","")
    df['votes'] = df['votes'].astype('int')
    df['metascore'] = df['metascore'].astype('float64')
    
    #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()

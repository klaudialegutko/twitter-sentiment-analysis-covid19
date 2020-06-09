## **Real-time sentiment analysis of tweets related to Covid-19 deployed with Flask and plotly/Dash**
### To run it:
1. Setup Twitter Developer account (https://developer.twitter.com/en) and store api keys and access tokens in credentials.py.
2. In order to extract tweets, I used tweepy to access Twitter API and stored it in mySQL. After installing all the dependencies and creating mySQL table, make changes to mySQL connection by providing database name and password.

``` 
con = mysql.connector.connect(host = 'localhost',
database='######', user='root', password = '######', charset = 'utf8') 
 ```

3. Next is sentiment analysis and its results. For sentiment analysis I used TextBlob, displayed it with Dash and deployed using Flask. Same as previously, after installing all the dependencies, change mySQL connection info in app.py to your own, and run the script. 
4. Type localhost in browser and real-time sentiment analysis should be displayed. 

### Dashboard includes:
- sentiment analysis graph.
- most common words bar chart.
- geographical distribution of where tweets are coming from.




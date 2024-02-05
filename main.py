import sqlite3
import httpx
from bs4 import BeautifulSoup

def main() -> None:
    URL = "https://cmr24.by/account/search?version=1"
    COOKIES = "advanced-frontend=e3122e454e9fb4cc4b9062f0ae22de97; _csrf=7410079a4b294a254211144664a11e8faba3cee9c4fee25d31105cdba825bc13a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22TVq88t1o3338RmUrZjOL6YanyHUrzkwg%22%3B%7D; _ym_uid=1706618631395660289; _ym_d=1706618631; _fbp=fb.1.1706618630689.400408766; _gcl_au=1.1.2024325695.1706618631; _ga=GA1.2.1989610241.1706618631; _ga_N2ZWBFJ02B=GS1.1.1707321939.4.0.1707321939.60.0.0; SearchForm=529b578e43deae05e08edd05b05114138a3e2028ba1ca73f23bd940da4092e25a%3A2%3A%7Bi%3A0%3Bs%3A10%3A%22SearchForm%22%3Bi%3A1%3Bs%3A336%3A%22%7B%221%22%3A%7B%22Type%22%3A0%2C%22cityFrom%22%3A282%2C%22cityTo%22%3A538%2C%22regionFrom%22%3A%5B%221602269%22%5D%2C%22regionTo%22%3A%5B%221600001%22%5D%2C%22countryFrom%22%3A3%2C%22countryTo%22%3A3%2C%22dateFrom%22%3A%2208.02.2024%22%2C%22dateTo%22%3A%2212.01.2024%22%2C%22Weight%22%3A%7B%22from%22%3A%22%22%2C%22to%22%3A10%7D%2C%22Volume%22%3A%7B%22from%22%3A%22%22%2C%22to%22%3A%22%22%7D%2C%22FilterType%22%3A%22%22%2C%22idBodytype%22%3A%220%22%2C%22emptyRouteText%22%3A%22%22%2C%22UserType%22%3A0%2C%22LoadType%22%3A%22-1%22%7D%2C%222%22%3A%5B%5D%2C%223%22%3A%5B%5D%2C%224%22%3A%5B%5D%2C%225%22%3A%5B%5D%7D%22%3B%7D"
    
    headers = {"Cookie": COOKIES}

    res = httpx.get(URL, headers=headers)
    
    soup = BeautifulSoup(res.text, 'html.parser')
    list = []
    inserted = []

    for row in soup.find_all("tr", class_="search-table-mobile-size"):
        list.append(row.get('trid'))

    con = sqlite3.connect("./notice_telegram/db.sqlite3")
    cur = con.cursor()
    for row in list:
        cur.execute("INSERT OR IGNORE INTO trid VALUES(?) RETURNING id", (row,))
        res = cur.fetchone()
        if res:
            inserted.append(res)
    con.commit()
    con.close()


    print(inserted)

if __name__ == "__main__":
    con = sqlite3.connect("./notice_telegram/db.sqlite3")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS trid(id INTEGER PRIMARY KEY)")
    con.commit()
    con.close()


    main()
    main()


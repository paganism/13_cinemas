import requests
from bs4 import BeautifulSoup
import re
import random


def fetch_proxy():
    proxy_url = 'http://freeproxy-list.ru/api/proxy?anonymity=false&token=demo'
    proxy_list = requests.get(proxy_url).text.split('\n')
    return proxy_list


def fetch_afisha_page():
    respond = requests.get('http://www.afisha.ru/msk/schedule_cinema/')
    return respond


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html.text, 'html.parser')
    cinemas = soup.find(class_='cards cards-grid')
    count_cinemas = []
    for item in cinemas.find_all('div', {'itemprop': "address"}):
        count = re.findall(r'\d+', str(item))
        # print(count)
        count_cinemas.append(count[0])
    title_list = []
    for i in cinemas.find_all('h3', {'class': 'card__title'}):
        # print(i.text.replace('«','').replace('»',''))
        title_list.append(i.text.strip().replace('«', '').replace('»', ''))
    mixed_dict = dict(zip(title_list, count_cinemas))
    return mixed_dict


def fetch_movie_info(movie_title, proxies):
    kp_url = 'https://www.kinopoisk.ru/index.php'
    payload = {'kp_query': movie_title}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/42.0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
    }
    proxy = {"http": random.choice(proxies)}
    print(proxy)
    print(movie_title)
    raw_search_info = requests.get(kp_url, params=payload, headers=headers, proxies=proxy)
    soup = BeautifulSoup(raw_search_info.text, 'html.parser')
    try:
        return soup.find('a', text=movie_title)['data-id']
    except TypeError:
        return soup.find('a', {'data-title': movie_title})['data-id']



def get_movie_rating(movie_title, proxies):
    kp_url = 'https://www.kinopoisk.ru/index.php?first=yes&what=&kp_query='
    # print(kp_url)
    # headers = {'User-Agent': random.choice(user_agent)}
    payload = {'kp_query': movie_title}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/42.0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
    }
    proxy = {"http": random.choice(proxies)}
    raw_movie_info = requests.get(kp_url, params=payload, headers=headers, proxies=proxy)
    try:
        soup = BeautifulSoup(raw_movie_info.text, 'html.parser')
        rating_ball = float(soup.find('span', class_='rating_ball').get_text())
        rating_count = soup.find('span', class_='ratingCount').get_text().replace(' ', '')
        return rating_ball, rating_count
    except:
        return '0', '0'


def get_element(element):
    return float(element[1])


def output_movies_to_console_dict(movie_dict):
    val_list = movie_dict.values()
    sorted_val = reversed(sorted(val_list, key=get_element))
    for val in sorted_val:
        for movie, info in movie_dict.items():
            if info == val:
                print('-' * 25)
                print('movie_title: {}'.format(movie), '\n',
                      'count_of_cinema: {}'.format(info[0]), '\n',
                      'rating: {}'.format(info[1]), '\n',
                      'votes_count: {}'.format(info[2]))


def output_movies_to_console(movie_list, top):
    sorted_list = sorted(movie_list, key=get_element)
    lentht = len(sorted_list)
    delimiter = '-' * 30
    for title, cinemas, rating, votes in reversed(sorted_list[top:lentht:1]):
        print(delimiter)
        print('Movie name: {}'.format(title))
        print('Count of cinemas: {}'.format(cinemas))
        print('Rating: {}'.format(rating))
        print('Count of votes: {}'.format(votes))


if __name__ == '__main__':
    content = fetch_afisha_page()
    titles = parse_afisha_list(content)
    proxies = fetch_proxy()
    #movie_dict = {}
    movie_list = []
    for movie, count_of_cinema in titles.items():
        rating_ball, rating_count = get_movie_rating(movie, proxies)
        # movie_dict[movie] = [count_of_cinema, rating_ball, rating_count]
        movies = [movie, count_of_cinema, rating_ball, rating_count]
        # print(movies)
        movie_list.append(movies)
    print(movie_list[0], movie_list[1], movie_list[2], movie_list[3])
    top = 10
    output_movies_to_console(movie_list, top)

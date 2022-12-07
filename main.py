import requests
import re
from bs4 import BeautifulSoup
from fake_headers import Headers
from time import sleep
import json

headers = Headers(os='win', browser='chrome')


HOST = 'https://spb.hh.ru'
ARTICLES = f'{HOST}/search'

def get_page(url):
    return requests.get(url, headers=headers.generate()).text

def job_screening(link):
    article_html = get_page(link)
    soup = BeautifulSoup(article_html, features='lxml')
    article = soup.find(class_="vacancy-description").find_all('ul')
    articl_ = re.sub(r'(\<.*?\>)', '', str(article))
    if re.search('Django', articl_) and re.search('Flask', articl_):
        return True

def parser_article(article_tag): 
    title = article_tag.find('h3').find('a').text
    link = article_tag.find('h3').find('a')['href']
    company = article_tag.find(class_='vacancy-serp-item__meta-info-company').find('a').text
    city = re.search('\w+', article_tag.find(class_='vacancy-serp-item__info').find('div', attrs={"data-qa": "vacancy-serp__vacancy-address"}).text).group()
    try:
        salary = article_tag.find('div', class_="vacancy-serp-item-body__main-info").find('span', attrs={"data-qa": "vacancy-serp__vacancy-compensation"}).text
    except:
        salary = 'По результатам собеседования'

    return {
        'title': title,
        'link': link,
        'company': company,
        'citi': city,
        'salary': salary
    }

def parse_all_jobs_pages(num_pages):
    main_html = get_page(f'{ARTICLES}/vacancy?text=python&area=1&area=2&page={num_pages}&hhtmFrom=vacancy_search_list')
    soup = BeautifulSoup(main_html, features='lxml')
    articles = soup.find_all(class_='serp-item')
    jobs_list = []
    for article in articles:
        sleep(0.33)
        link = article.find('h3').find('a')['href']
        if job_screening(link):
           jobs_list.append(parser_article(article))       
    
    if len(jobs_list) > 0:
        return jobs_list

def write_file(jobs_list):
    with open('jobs_list.json', 'w', encoding='utf-8') as f:
        json.dump(jobs_list, f, ensure_ascii=False, indent=2)
    return    

def parse_num_pages():
    final_list_vacancies = []
    for i in range(10):
        sleep(0.33)
        vacancies = parse_all_jobs_pages(i)
        if vacancies:
            final_list_vacancies.append(vacancies)
    return final_list_vacancies


if __name__ == '__main__':
    itog_list = parse_num_pages()
    write_file(itog_list)
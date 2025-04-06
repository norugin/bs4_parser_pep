import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import DOWNLOADS_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URl
from exceptions import SectionNotFoundException
from outputs import control_output
from utils import get_response, find_tag


def make_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    return BeautifulSoup(response.text, features='lxml')


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = make_soup(session, whats_new_url)

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = make_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    soup = make_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div', attrs={'class': {'sphinxsidebarwrapper'}})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise SectionNotFoundException
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        try:
            version = text_match.group('version')
            status = text_match.group('status')
        except Exception:
            version = a_tag.text
            status = ''
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = make_soup(session, downloads_url)

    pdf_a4_tag = find_tag(soup, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = make_soup(session, PEP_URl)
    pep_statuses = list(soup.find_all('abbr'))
    pep_statuses = [tag for tag in pep_statuses
                    if tag.text not in ['Active', 'Informational']]
    pep_links = soup.find_all('a', attrs={'class': 'pep reference internal'})
    del pep_links[0]
    pep_links = pep_links[::2]
    results = [('Статус', 'Количество')]
    status_sum = {}
    for i in tqdm(range(len(pep_statuses))):
        pep_status = pep_statuses[i]
        pep_link = pep_links[i]
        if len(pep_status.text) == 2:
            main_page_status = EXPECTED_STATUS[pep_status.text[1]]
        else:
            main_page_status = EXPECTED_STATUS['']
        pep_link = pep_link['href']
        pep_page_url = urljoin(PEP_URl, pep_link)
        page_soup = make_soup(session, pep_page_url)
        page_status = find_tag(page_soup, 'abbr').text
        if page_status not in main_page_status:
            logging.info(pep_link)
            logging.info(f'Статус в карточке {page_status}')
            logging.info(f'Ожидаемые статусы: {main_page_status}')
        status_sum[page_status] = status_sum(page_status, 0) + 1
    results.extend(status_sum.items())
    total_sum = sum(status_sum.values())
    results.append(('Total', total_sum))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info('Парсер запущен!')
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(f'Аргументы командной строки: {args}')
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.exception(f'Критическая ошибка: {str(error)}')
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()

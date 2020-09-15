#!/usr/bin/env python
#
# Script to download all documents from chamilo

import cgi
import getpass
import http.cookiejar as cookielib
import re
import sys
from pathlib import Path
from time import sleep
import argparse

import mechanize
from bs4 import BeautifulSoup as bs

# Global variables
browser = None

BASE_URL = 'https://cas-simsu.grenet.fr/login?service=http%3A%2F%2Fchamilo.univ-grenoble-alpes.fr%2Fmain%2Fauth%2Fcas%2Flogincas.php'

valid_course_re = re.compile(".*courses\/[^UGA.*].*")
valid_document_re = '/main/document/document.php'
valid_file_ext = ['.jpg', '.png', '.docx', '.pdf']


def get_credentials(username, password):
    '''Ask the user for credentials in case they are not provided.'''
    if username is None:
        username = input('User: ')
    if password is None:
        password = getpass.getpass(prompt='Password: ')

    return (username, password)


def setup_browser():
    '''Create the browser and configure it properly.'''
    browser = mechanize.Browser()
    cookiejar = cookielib.LWPCookieJar()
    browser.set_cookiejar(cookiejar)
    browser.set_handle_equiv(True)
    browser.set_handle_gzip(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)
    browser.set_handle_refresh(
        mechanize._http.HTTPRefreshProcessor(), max_time=1
    )
    browser.addheaders = [
        ('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36')
    ]
    return browser


def download_file(file_path, file_url):
    '''Download the file to the given path.'''
    res = browser.open(file_url)
    file = open(file_path, 'wb')
    file.write(res.read())
    file.close()


def get_courses(courses_page, blacklist=[]):
    '''Extract all courses and their url from the main page of chamilo.'''
    # TODO: Allow to blacklist courses
    courses = set()
    courses_soup = bs(courses_page, "html.parser")
    headers = courses_soup.findAll('h4', class_='course-items-title')
    for course in headers:
        a = course.find('a', href=True)
        if valid_course_re.search(a['href']):
            course_name = a.text.strip()
            courses.add((course_name, a['href']))
    return courses


def get_documents_route(course_page):
    '''Given a course page, extract its documents folder url.'''
    tags = course_page.findAll('a', href=True)
    docs = list(filter(lambda a: a.text.strip() == 'Documents', tags))
    return None if not docs else docs[0]['href']


def extract_files(base_path, course_name, page_url):
    '''Recursively extract all documents names and urls from a course page.'''
    files = set()
    res = browser.open(page_url)
    course = bs(res, 'html.parser')
    cdheader = res.get('Content-Disposition', None)
    if cdheader is not None:
        value, params = cgi.parse_header(cdheader)
        if value == 'attachment':
            files.add((base_path / course_name, page_url))
            return files

    table = course.find('table')
    if table is None:
        return files

    # All file links are inside the table
    for td in table.findAll('td'):
        a = td.find('a', href=True)
        if not a or not a.get('href'):
            continue

        file_name = a.text.strip()
        file_url = a['href']
        # Don't add the `go back` link
        if file_name == course_name or not file_name:
            continue

        # Dirty way to know if the url is for a file or for a folder
        file_extensions = file_name.split('.')
        file_path = base_path / course_name / file_name

        if len(file_extensions) < 2 and len(file_extensions[-1]) < 3:
            new_files = extract_files(base_path / course_name, file_name, file_url)
            files = files.union(new_files)
        else:
            files.add((file_path, file_url))


    return files


def run(base_path, username, password):
    '''
    Entry point of the scraper.
    Ask the user for credentials, login and
    download all documents from every course.
    '''

    # Login to the main page
    username, password = get_credentials(username, password)
    browser.open(BASE_URL)
    browser.select_form(nr=0)
    browser.form['username'] = username
    browser.form['password'] = password
    res = browser.submit()

    # Get all courses
    courses = get_courses(res)
    if not courses:
        # TODO: Better error handling
        print("There was a problem with the login")
        sys.exit(1)

    for course_name, course_href in courses:
        print(f'Course: {course_name}')

        res = browser.open(course_href)
        course = bs(res, 'html.parser')
        docs_link = get_documents_route(course)

        if not docs_link:
            print()
            continue

        files = extract_files(base_path, course_name, docs_link)
        for file_name, file_url in files:
            if file_name.exists():
                print(f'[EXISTS] {file_name.relative_to(base_path)}')
            else:
                parent = file_name.parent
                parent.mkdir(parents=True, exist_ok=True)
                print(f"[DOWNLOAD] {file_name.relative_to(base_path)}")
                download_file(file_name, file_url)
                sleep(1)  # Throttle the connection
        print()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='UGA Chamilo scraper')
    ap.add_argument("-d", "--dir", required=False, default='.',
                    help='''Directory to download all courses. Defaults to the current directory.''')
    ap.add_argument("-u", "--username", required=False, help="Username")
    ap.add_argument("-p", "--password", required=False, help="Password")
    args = vars(ap.parse_args())

    base_dir = Path(args['dir']).absolute()
    browser = setup_browser()
    run(base_dir, args['username'], args['password'])

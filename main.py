#!/usr/bin/env python
#
# Script to download all documents from chamilo

import mechanize
import re
import getpass
import sys
import os
from pathlib import Path


# Global variables
BASE_URL = 'https://cas-simsu.grenet.fr/login?service=http%3A%2F%2Fchamilo.univ-grenoble-alpes.fr%2Fmain%2Fauth%2Fcas%2Flogincas.php'
br = None


class ChamiloUGAScraper:

    course_re = re.compile('.*courses\/[^UGA.*].*')

    def __init__(self):
        self.browser = mechanize.Browser()
        self.__setup_browser()
        self.base_url = BASE_URL
        self.courses = []
        self.base_path = Path('.').resolve()

    def get_credentials(self):
        username = input('User: ')
        password = getpass.getpass(prompt='Password: ')
        return (username, password)

    def __setup_browser(self):
        cookie_jar = mechanize.LWPCookieJar()
        opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookie_jar))
        mechanize.install_opener(opener)
        self.browser.set_handle_robots(False)
        self.browser.set_handle_refresh(False)
        self.browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self.browser.addheaders = [('User-agent', 'Firefox')]

    def download_file(self):
        pass

    def get_courses(self):
        for link in self.browser.links():
            if self.course_re.search(link.url):
                self.courses.append(link)

    def run(self):
        # Log the user to access all courses
        username, password = self.get_credentials()

        self.browser.open(self.base_url)
        self.browser.select_form(nr=0)
        self.browser.form['username'] = username
        self.browser.form['password'] = password

        # TODO: Handle errors
        res = self.browser.submit()

        self.get_courses()
        course = None
        for c in self.courses:
            if c.text == 'M2-EEA-WICS Wireless Communications':
                course = c

        # TODO: Download courses asynchronously
        # for course in list(reversed(self.courses))[0]:
        course_path = Path(course.text)
        course_path.mkdir(parents=True, exist_ok=True)

        # Enter into `Documents` directory and download everything
        print(f'Accessing course: {course.text}')
        os.chdir(course_path)
        request = self.browser.click_link(course)
        response = self.browser.follow_link(course)
        docs_link = None
        for l in self.browser.links():
            if l.text == 'Documents':
                docs_link = l

        request = self.browser.click_link(docs_link)
        response = self.browser.follow_link(docs_link)

        document_re = '/main/document/document.php'
        # TODO: Useful links contain title
        for link in self.browser.links():
            attrs = dict(link.attrs)
            print(attrs)
            if document_re in l.url and attrs['title']:
                print(l)

        os.chdir(self.base_path)



# def download_file(doc_url, filename='', referer=''):
#     '''
#     Download the given file
#     '''
#     res = br.click_link(doc_url)
#     if referer:
#         res.add_header("Referer", referer)

#     doc_res = br.open(res)

#     # TODO: Check if file exists
#     if Path(filename).exists():
#         print(f'File {filename} already exists')
#     else:
#         f = open(filename, 'wb')
#         f.write(doc_res.read())
#         f.close()
#         print(f'File {filename} has been downloaded')
#     br.back()


# # TODO: Handle all courses
# for course in courses:
#     print(f'Course: {course.text}')
#     course_dir = Path(course.text)
#     course_dir.mkdir(parents=True, exist_ok=True)

# sys.exit(0)
# request = br.click_link(link)
# response = br.follow_link(link)

# print('--------------------')
# print('Entered in Signal integrity course')

# # Open the documents pages
# docs = None
# for l in br.links():
#     if l.text == 'Documents':
#         docs = l


# request = br.click_link(docs)
# response = br.follow_link(docs)

# print('--------------------')
# print('Entered in Signal integrity documents')

# # This page should display the documents list
# slides = None
# slides_re = re.compile('^Slides.*')
# for l in br.links():
#     if slides_re.search(l.text):
#         slides = l

# request = br.click_link(slides)
# response = br.follow_link(slides)

# print('--------------------')
# print('Entered in Signal integrity slides listing')

# for l in br.links():
#     if 'pdf' in l.url and l.text:  # Is it neccesary to check for pdf?
#         name = l.text + '.pdf'
#         download_file(l, filename=name, referer=br.geturl())


if __name__ == '__main__':
    scraper = ChamiloUGAScraper()
    scraper.run()

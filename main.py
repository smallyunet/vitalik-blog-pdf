# -*- coding:utf-8 -*-

import os
import re
import time
import logging
import pdfkit
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger
import os.path
import shutil
from datetime import date

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""

def get_url_list():
    response = requests.get("http://vitalik.ca//")
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
    for v in soup.find_all(class_="post-link"):
        url = "http://vitalik.ca/" + v.get('href')
        urls.append(url)
    return urls


def parse_url_to_html(url, name):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        inner = soup.find_all(class_="markdown-body")
        if inner.__len__() == 0:
            return False

        body = inner[0]
        html = str(body)

        pattern = "(<img .*?src=\")(.*?)(\")"
        def func(m):
            return m.group(0).replace("../../../..", "https://vitalik.ca")
        html = re.compile(pattern).sub(func, html)

        html = html_template.format(content=html)
        with open(name, 'wb') as f:
            f.write(html.encode())
        return True

    except Exception as e:
        logging.error("parse error ", exc_info=True)


def save_pdf(htmls, file_name):
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'minimum-font-size': 12,
    }
    try:
        pdfkit.from_file(htmls, file_name, options=options)
    except Exception as e:
        logging.error("covert error ", exc_info=True)


def main():
    shutil.rmtree("html") if os.path.exists("html") else None
    os.mkdir("html") if not os.path.exists("html") else None
    shutil.rmtree("pdf") if os.path.exists("pdf") else None
    os.mkdir("pdf") if not os.path.exists("pdf") else None

    start = time.time()
    urls = get_url_list()
    wrongUrl = []
    for index, url in enumerate(urls):
        name = str(index) + ".html"
        name = os.path.join("html", name)
        res = parse_url_to_html(url, name)
        if res is False:
            wrongUrl.append(str(index))
        print(u"download " + str(index) + ' html')
    
    htmls = []
    pdfs = []
    print("wrongUrl", wrongUrl)
    for i in range(0, urls.__len__()):
        if str(i) in wrongUrl:
            continue
        htmlName = str(i) + ".html"
        htmlName = os.path.join("html", htmlName)
        name = str(i) + '.pdf'
        name = os.path.join("pdf", name)
        htmls.append(htmlName)
        pdfs.append(name)

        save_pdf(htmlName, name)
        print(u"covert " + str(i) + ' html')

    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))
        print(u"merge " + str(i) + ' pdf')

    todays_date = date.today()
    name = "vitalik-blog-" + str(todays_date) + ".pdf"
    output = open(name, "wb")
    merger.write(output)

    print(u"success")

    # for html in htmls:
    #     os.remove(html)
    #     print(u"delete " + html)

    # for pdf in pdfs:
    #     os.remove(pdf)
    #     print(u"delete " + pdf)

    total_time = time.time() - start
    print(u"total spend：%f second" % total_time)


if __name__ == '__main__':
    main()

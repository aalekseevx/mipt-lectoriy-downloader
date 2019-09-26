from sys import argv
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import urljoin
from re import compile, sub
import subprocess
import os


def beautify_name(name):
    return (compile('[^a-zA-Zа-яА-Я ]')).sub('', name)

def download_lecture(url, path):
    response = get(url)
    if response.status_code != 200:
        print ("Error. Status code not 200, while processing {}".format(url))
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    video_url = soup.find('video').find('source').get('src')[2:-2]
    subprocess.Popen(["wget", "-O", path, video_url])


def download_series(url):
    response = get(url)
    if response.status_code != 200:
        print ("Error. Status code not 200, while processing {}".format(url))
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('div', class_=r'\"object-info\"').find('h1').text

    lectures_set = set()
    for lecture_block in soup.findAll('div', class_=r'\"lecture-block\"'):
        lecture_title = lecture_block.find('div', class_=r'\"lecture-title\"')
        lecture_classes = lecture_title.get("class")

        if type(lecture_classes) != list:
            continue

        lectures_order = (lecture_block.find('div', class_=r'\"lecture-order\"').text).zfill(2)
        link_tag = lecture_title.find('a')
        url = urljoin(url, link_tag.get('href')[2:-2])
        name = lectures_order + '. ' + beautify_name(link_tag.text)
        lectures_set.add((url, name))

    directory = os.path.join('.', title)
    if not os.path.exists(directory):
        os.makedirs(directory)

    for lect_url, lect_name in lectures_set:
        download_lecture(lect_url, os.path.join(directory, lect_name) + '.mp4')


if __name__ == "__main__":
    if len(argv) == 1:
      print("Usage: python3 main.py [links]")   
      exit(0)
    for url in argv[1:]:
      download_series(url)
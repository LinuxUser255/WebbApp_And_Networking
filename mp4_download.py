#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Specify the URL from which to download between the double quotes
# Example: 
# archive_url = "http://videowebsite.com/"
archive_url = ""

def get_video_links():
    r = requests.get(archive_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    links = soup.findAll('a')
    video_links = [archive_url + link['href'] for link in links if link['href'].endswith('mp4')]
    return video_links

def download_video_series(video_links):
    for link in video_links:
        file_name = link.split('/')[-1]

        print("Downloading file:%s" % file_name)
        r = requests.get(link, stream=True)

        # download started
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        print("%s downloaded!\n" % file_name)

    print("All videos downloaded!")
    return


if __name__ == "__main__":
    # getting all video links
    video_links = get_video_links()

    # download all videos
    download_video_series(video_links)

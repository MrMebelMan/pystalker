#!/usr/bin/env python3

from sys import argv
from requests import get as requests_get
from threading import Thread


class Stalker:
    def __init__(self, user_names: list):
        if not user_names:
            raise ValueError('Provide at least one username.')
        self.user_names = user_names
        self.headers = {}
        self.results = None

    def check_by_response_code(self, url: str, results: list):
        r = requests_get(url, headers=self.headers, verify=True, allow_redirects=True)
        if r.status_code in [404, 410, 429]:
            return
        elif r.status_code != 200:
            print('%s: Unknown status code: %d' % (url, r.status_code))
            return
        print(r.url)
        results.append(r.url)

    def check_by_content(self, url: str, content: str, results: list):
        r = requests_get(url, headers=self.headers, verify=True, allow_redirects=True)

        if content[0] == '^':
            content = content[1:]
            fail_condition = content not in r.text
        else:
            fail_condition = content in r.text

        if r.status_code != 200 or fail_condition:
            return
        print(r.url)
        results.append(r.url)

    def check_by_redirect(self, url: str, results: list):
        r = requests_get(url, headers=self.headers, verify=True, allow_redirects=False)
        if r.status_code == 302:
            return
        print(r.url)
        results.append(r.url)

    def stalk(self):
        results = []
        for username in self.user_names:
            urls = [
                'https://steemit.com/@%s',
                'https://youtube.com/user/%s', 
                'https://reddit.com/user/%s',
                'https://vk.com/%s',
                'https://twitter.com/%s',
                'https://www.instagram.com/%s',
                'https://ok.ru/%s',
                'https://ask.fm/%s',
                'https://www.flickr.com/people/%s',
                'https://mastodon.social/@%s',
                'https://wikipedia.org/wiki/User:%s',
                'https://www.quora.com/%s',
                'https://github.com/%s',
                'https://habr.com/ru/users/%s',
                'https://soundcloud.com/%s',
                'https://vimeo.com/%s',
                'https://disqus.com/by/%s',
                'https://deviantart.com/%s',
                'https://about.me/%s',
                'https://bitbucket.org/%s',
                'https://imgur.com/user/%s',
                'https://flipboard.com/@%s',
                'https://open.spotify.com/user/%s',
                'https://keybase.io/%s',
                'https://tradingview.com/u/%s',
                'https://%s.livejournal.com/',
                'https://codecademy.com/%s',
                'https://medium.com/@%s',
                'https://tripadvisor.com/Profile/%s',
                'https://%s.slack.com/',
                'https://pypi.org/user/%s',
            ]
            urls_redirect = [
              'https://pastebin.com/u/',
              'https://en.gravatar.com/'
            ]
            urls_content = {
                'https://www.facebook.com/':      '^| Facebook',
                'https://pinterest.com/':         'name="og:title" content="Pinterest"',
                'https://t.me/':                  'content="Telegram: Contact',
                'https://gab.com/':               '<meta property="og:title" content="Gab"',
                'https://www.mixcloud.com/':      'Page Not Found | Mixcloud',
                'https://steamcommunity.com/id/': 'profile could not be found',
            }
            threads = []

            for url in urls:
                thread = Thread(target=self.check_by_response_code, args=(url % username, results))
                thread.start()
                threads.append(thread)

            for url in urls_redirect:
                thread = Thread(target=self.check_by_redirect, args=(url + username, results))
                thread.start()
                threads.append(thread)

            for url, content in urls_content.items():
                thread = Thread(target=self.check_by_content, args=(url + username, content, results))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        return sorted(results)


if __name__ == '__main__':
    user_names = []
    for i in range(1, len(argv)):
        user_names.append(argv[i])

    stalker = Stalker(user_names)
    stalker.stalk()


import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import requests
from bs4 import BeautifulSoup


HEADERS = {'user-agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
           'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    html = html.text
    soup = BeautifulSoup(html, 'html.parser')
    student_table = soup.find_all('table', class_='table table-bordered table-structure table-hover')[-1]

    content = []

    for student in student_table.find_all('tbody'):
        rows = student.find_all('tr')
        for row in rows:
            name = row.find_all('td', class_='align-middle')[1].text.split('Подано так же на:')[0].strip()
            points = row.find_all('td', class_='align-middle')[2].text.strip()
            allow = row.find_all('td', class_='align-middle')[7].text.strip()
            if allow == '✓':
                content.append({'name': name, 'points': int(points)})

    return content


def parse(url):
    html = get_html(url)
    if html.status_code == 200:
        content = get_content(html)
        students = sorted(content, key=lambda k: -k['points'])
        result = ''
        count = 0
        for student in students:
            count += 1
            result += f'№{str(count)} - {student["name"]} - {student["points"]} баллов' + '\n'
            if count % 75 == 0:
                result += '|'
        return result
    else:
        return 'ERROR'


vk = vk_api.VkApi(token="")
vk._auth_token()
vk.get_api()
group_id = 203434371
longpoll = VkBotLongPoll(vk, group_id)


def send_message(peer_id, text, keyboard=None):
    vk.method("messages.send", {"peer_id": peer_id, "message": text,
                                "random_id": random.randint(-9223372036854775807, 9223372036854775807),
                                "keyboard": keyboard})


while True:
    for event in longpoll.listen():
        try:
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object['text'].startswith('https://abitur.sstu.ru/'):
                    parse_info = parse(event.object['text']).split('|')
                    for info in parse_info:
                        send_message(peer_id=event.object['peer_id'], text=info)


        except requests.exceptions.ReadTimeout:
            print('ConnectionError')
            continue

# -*- coding: utf-8 -*-
import json
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response

from urllib import parse

from datetime import datetime
from datetime import timedelta

from random import randint

app = Flask(__name__)

slack_token = "My_slack_token"
slack_client_id = "My_slack_client_id"
slack_client_secret = "My_slack_client_secret"
slack_verification = "My_slack_verification"
sc = SlackClient(slack_token)

proverb_flag = False
proverb_answer = []


# 완결 웹툰 크롤링 함수
def _crawl_finish_webtoon():
    response = []
    response.append("[네이버 완결 웹툰 추천 :)]\n")

    url = "https://comic.naver.com/webtoon/finish.nhn?order=ViewCount&view=image"

    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    webtoon_titles = []
    for webtoon in soup.find_all("div", class_="thumb"):
        if len(webtoon_titles) == 10:
            break
        webtoon_titles.append(webtoon.a["title"])
    print(webtoon_titles)

    webtoon_authors = []
    for author in soup.find_all("dd", class_="desc"):
        if len(webtoon_authors) == 10:
            break
        webtoon_authors.append(author.a.get_text())
    print(webtoon_authors)

    webtoon_links = []
    for webtoon in soup.find_all("div", class_="thumb"):
        if len(webtoon_links) == 10:
            break
        webtoon_links.append("https://comic.naver.com/" + webtoon.a["href"])
    print(webtoon_links)

    for i in range(len(webtoon_titles)):
        response_txt = str(i + 1) + ": "
        response_txt += webtoon_titles[i] + " / "
        response_txt += webtoon_authors[i] + " -> "
        response_txt += webtoon_links[i]
        response.append(response_txt)

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(response)


# 요일별 웹툰 크롤링 함수
def _crawl_day_webtoon(day):
    print(day)
    response = []

    if day == 'no':
        response.append("무슨 요일의 웹툰을 알려드릴까요? (입력 예시: 월요일 웹툰)")
        return u'\n'.join(response)

    if day == 'mon':
        response.append("[네이버 월요일 웹툰 추천 :)]\n")
    elif day == 'tue':
        response.append("[네이버 화요일 웹툰 추천 :)]\n")
    elif day == 'wed':
        response.append("[네이버 수요일 웹툰 추천 :)]\n")
    elif day == 'thu':
        response.append("[네이버 목요일 웹툰 추천 :)]\n")
    elif day == 'fri':
        response.append("[네이버 금요일 웹툰 추천 :)]\n")
    elif day == 'sat':
        response.append("[네이버 토요일 웹툰 추천 :)]\n")
    elif day == 'sun':
        response.append("[네이버 일요일 웹툰 추천 :)]\n")

    url = "https://comic.naver.com/webtoon/weekdayList.nhn?week=" + day

    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    webtoon_titles = []
    for webtoon in soup.find_all("div", class_="thumb"):
        if len(webtoon_titles) == 13:
            break
        webtoon_titles.append(webtoon.a["title"])
    webtoon_titles = webtoon_titles[3:]

    webtoon_authors = []
    for author in soup.find_all("dd", class_="desc"):
        if len(webtoon_authors) == 13:
            break
        webtoon_authors.append(author.a.get_text())
    webtoon_authors = webtoon_authors[3:]

    webtoon_links = []
    for webtoon in soup.find_all("div", class_="thumb"):
        if len(webtoon_links) == 13:
            break
        webtoon_links.append("https://comic.naver.com/" + webtoon.a["href"])
    webtoon_links = webtoon_links[3:]

    for i in range(len(webtoon_titles)):
        response_txt = str(i + 1) + ": "
        response_txt += webtoon_titles[i] + " / "
        response_txt += webtoon_authors[i] + " -> "
        response_txt += webtoon_links[i]
        response.append(response_txt)

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(response)


# 유튜브 실시간 인기 Top 10 크롤링 함수
def _crawl_youtube():
    print("youtube crawling....")

    response = []
    response.append("유튜브 실시간 인기 Top 10 영상 리스트입니다! :)\n")

    url = "https://www.youtube.com/feed/trending"

    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    video_titles = []
    for video in soup.find_all("a", class_="yt-ui-ellipsis"):
        if len(video_titles) == 10:
            break
        video_titles.append(video["title"])

    video_links = []
    for video in soup.find_all("a", class_="yt-ui-ellipsis"):
        if len(video_links) == 10:
            break
        video_links.append("https://www.youtube.com" + video["href"])

    for i in range(len(video_titles)):
        response_txt = str(i + 1) + ": "
        response_txt += video_titles[i] + " -> "
        response_txt += video_links[i]
        response.append(response_txt)

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(response)


# 띠별 운세 크롤링 함수
def _crawl_lucky(text):
    game = []
    lists = []

    name = ""

    if text == "no":
        lists.append("미안하지만 그런 띠 없어요ㅠㅠ")
        return u'\n'.join(lists)

    if "쥐" in text:
        name = parse.quote("쥐")
    elif "소" in text:
        name = parse.quote("소")
    elif "호랑이" in text:
        name = parse.quote("호랑이")
    elif "토끼" in text:
        name = parse.quote("토끼")
    elif "용" in text:
        name = parse.quote("용")
    elif "뱀" in text:
        name = parse.quote("뱀")
    elif "말" in text:
        name = parse.quote("말")
    elif "양" in text:
        name = parse.quote("양")
    elif "원숭이" in text:
        name = parse.quote("원숭이")
    elif "닭" in text:
        name = parse.quote("닭")
    elif "개" in text:
        name = parse.quote("개")
    elif "돼지" in text:
        name = parse.quote("돼지")

    url = "https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&query=%EC" + name \
          + "%EB%9D%A0%20%EC%9A%B4%EC%84%B8"

    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    # for i in soup.find_all("a", class_="title"):
    #     list_href.append("https://play.google.com" + i["href"])
    for bugs in soup.find_all("p", class_="text _cs_fortune_text"):
        game.append(bugs.get_text().replace("\n", ""))

    lists.append(parse.unquote(name) + "띠 운세 정보 : " + game[0])

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(lists)


# 게임 앱 Top 10 크롤링 함수
def _crawl_game_app():
    print("구글 플레이스토어 인기 게임 순위입니다.")

    url = "https://play.google.com/store/apps/collection/recommended_for_you_POPULAR_GAME?" + \
          "clp=ogoQCAQSBEdBTUUqAggCUgIIAQ%3D%3D:S:ANO1ljJUzaY&gsr=ChOiChAIBBIER0FNRSoCCAJSAggB:S:ANO1ljL9yJw"
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

    game = []
    link = []
    lists = []

    for bugs in soup.find_all("a", class_="title"):
        game.append(bugs.get_text())
    for i in soup.find_all("a", class_="title"):
        link.append("https://play.google.com" + i["href"])

    for i in range(10):
        lists.append(str(i+1) + "번 : " + game[i] + " / " + link[i])

    return u'\n'.join(lists)


# 속담 맞히기 게임
def _proverb_game():
    global proverb_answer
    global proverb_flag

    proverb_flag = True
    response = []

    proverbs_list = []

    urls = ["https://ko.wiktionary.org/w/index.php?title=%EB%B6%84%EB%A5%98:%ED%95%9C%EA%B5%AD%EC%96%B4_%EC%86%8D%EB%8B%B4",
            "https://ko.wiktionary.org/w/index.php?title=%EB%B6%84%EB%A5%98:%ED%95%9C%EA%B5%AD%EC%96%B4_%EC%86%8D%EB%8B%B4&pagefrom=%EB%88%84%EC%9B%8C%EC%84%9C+%EC%B9%A8+%EB%B1%89%EA%B8%B0#mw-pages"]

    for url in urls:
        req = urllib.request.Request(url)
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        for source_code in soup.find_all("div", class_="mw-category-group"):
            items = source_code.find_all("a")
            for item in items:
                proverbs_list.append(item["title"])

    answer = proverbs_list[randint(0, len(proverbs_list))]
    answer_list = answer.split()
    if len(answer_list) <= 2:
        response.append(answer_list[0])
        proverb_answer = [answer_list[1]]
    elif len(answer_list) > 4:
        response.append(answer_list[0] + " " + answer_list[1] + " " + answer_list[2])
        proverb_answer = []
        for i in range(3, len(answer_list)):
            proverb_answer.append(answer_list[i])
    else:
        response.append(answer_list[0] + " " + answer_list[1])
        proverb_answer = []
        for i in range(2, len(answer_list)):
            proverb_answer.append(answer_list[i])

    return u'\n'.join(response)


# 속담 맞힌지 확인
def _check_proverb_game(text):
    global proverb_answer
    response = []

    print(text.replace(" ", "").replace('<@UEWSGEUSD>', ''), ''.join(proverb_answer))
    print(text.replace(" ", "").replace('<@UEWSGEUSD>', '') == ''.join(proverb_answer))

    if text.replace(" ", "").replace('<@UEWSGEUSD>', '') == ''.join(proverb_answer):
        response.append("오~~ 정답이에요!")
    else:
        response.append("앗 정답은 [")
        response.append(' '.join(proverb_answer))
        response.append("]에요ㅠㅠ")

    return u' '.join(response)


# default 함수
def _default_answer():
    response = []
    response.append("반가워요 프로응답러입니다:)\n")
    response.append("- 오늘의 띠별 운세 보기")
    response.append("     예시) 쥐띠 운세")
    response.append("- 네이버 웹툰 Top 10 보기 (요일별 / 완결)")
    response.append("     예시) 목요일 웹툰 좀!")
    response.append("     예시) 완결 웹툰은?")
    response.append("- 실시간 인기 유튜브 영상 보기")
    response.append("     예시) 유튜브 인기 영상")
    response.append("- 게임 앱 Top 10 보기")
    response.append("     예시) 게임 앱 추천 좀 해주라")
    response.append("- 속담 맞히기")
    response.append("     예시) 속담")

    return u'\n'.join(response)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    global proverb_flag

    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        if proverb_flag:
            response = _check_proverb_game(text)
            proverb_flag = False
        else:
            if "완결" in text and "웹툰" in text:
                print("완결 웹툰")
                response = _crawl_finish_webtoon()
            elif "웹툰" in text:
                if "월" in text:
                    response = _crawl_day_webtoon("mon")
                elif "화" in text:
                    response = _crawl_day_webtoon("tue")
                elif "수" in text:
                    response = _crawl_day_webtoon("wed")
                elif "목" in text:
                    response = _crawl_day_webtoon("thu")
                elif "금" in text:
                    response = _crawl_day_webtoon("fri")
                elif "토" in text:
                    response = _crawl_day_webtoon("sat")
                elif "일" in text:
                    response = _crawl_day_webtoon("sun")
                else:
                    response = _crawl_day_webtoon("no")
            elif "유튜브" in text:
                response = _crawl_youtube()
            elif "운세" in text:
                if "쥐" in text:
                    response = _crawl_lucky("쥐")
                elif "쥐" in text:
                    response = _crawl_lucky("소")
                elif "호랑이" in text:
                    response = _crawl_lucky("호랑이")
                elif "토끼" in text:
                    response = _crawl_lucky("토끼")
                elif "용" in text:
                    response = _crawl_lucky("용")
                elif "뱀" in text:
                    response = _crawl_lucky("뱀")
                elif "말" in text:
                    response = _crawl_lucky("말")
                elif "양" in text:
                    response = _crawl_lucky("양")
                elif "원숭이" in text:
                    response = _crawl_lucky("원숭이")
                elif "닭" in text:
                    response = _crawl_lucky("닭")
                elif "개" in text:
                    response = _crawl_lucky("개")
                elif "돼지" in text:
                    response = _crawl_lucky("돼지")
                else:
                    response = _crawl_lucky("no")
            elif "게임" in text:
                response = _crawl_game_app()
            elif "속담" in text:
                response = _proverb_game()
            else:
                response = _default_answer()

        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    # if slack_event['event_time'] < (datetime.now() - timedelta(seconds=1)).timestamp():
    #     return make_response("this message is before sent.", 200, {"X-Slack-No-Retry": 1})

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":"application/json"})

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)

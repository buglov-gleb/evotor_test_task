# coding: utf-8

import requests
import re
from difflib import SequenceMatcher


# make an API call and get the response
def get_api_response(query):
    response = requests.get('http://jservice.io/api/random', params={'count': query})
    return response.json()

#initialize states to remember dialogue context
states = None

def chatbot():
    global states
    bye_pattern = r'(^q$|.*quit.*|bye.*)'
    range_pattern = r'^([123456789]\d?|100)$'
    play_pattern = r'(.*play.*|.*again.*|.*repeat.*)'
    while True:
        #initialize state history & greet
        if not states:
            states = ['start']
            query = input('Hey! I\'m a quiz-bot! Here\'s the rules:\n1. Enter the number of questions to ask (100 is max)\n2. You can try twice for each questions.\n3.Incomplete match is also a match!\nThat\'s it! How many questions you\'d like me to ask? (1-100)\n')
        #condition for the case of unexpected exit
        elif states[-1] == 'farewell':
            if query == 'y':
                print('Bye!')
                break
            else:
                states.append(states[-2])
                query = input('Let\'s continue then!\nMy last question is:\n' + questions_array[counter]['question'] +'\n')
        elif re.match(bye_pattern, query, re.IGNORECASE):
            if not re.search(r'^\d_asked$', states[-1]):
                states.append('farewell')
                print('Byeee!')
                break
            else:
                states.append('farewell')
                query = input('Sure you wanna quit? y/n\n')
        #if user entered number of questions
        elif re.match(range_pattern, query) and not re.search(r'^\d_asked$', states[-1]):
            questions_number = int(query)
            questions_array = get_api_response(questions_number)
            counter, score, attempts = 0, 0, 1
            states.append(str(counter) + '_asked')
            #used re.sub in answer assigning as we can get answers like <i>answer</i>
            answer = re.sub('<[^<]+?>', '', questions_array[counter]['answer'])
            query = input('Ok, so my first question is:\n' + questions_array[counter]['question'] + '\n')
        #if user is playing now
        elif re.match(r'\d_asked', states[-1]):
            #instead of incomplete match used SequenceMatcher
            if SequenceMatcher(None, query.lower(), answer.lower()).ratio() > 0.8:
                counter += 1
                score += 1
                attempts = 1
                if counter < questions_number:
                    answer = re.sub('<[^<]+?>', '', questions_array[counter]['answer'])
                    states.append(str(counter) + '_asked')
                    query = input('You\'re right\nNext question is:\n' + questions_array[counter]['question'] + '\n')
                else:
                    states.append('game_over')
                    query = input('Game over!\nYour score is ' + str(score) + ' out of ' + str(questions_number) + '\nIf you want to play again just type "repeat"\n')
            else:
                if attempts < 2:
                    attempts += 1
                    query = input('1st time not fine!\nLet me repeat the question again:\n' + questions_array[counter]['question'] + '\n')
                else:
                    counter += 1
                    if counter < questions_number:
                        attempts = 1
                        query = input('Not right this time, the answer is: ' + answer + '\nNext question is:\n' + questions_array[counter]['question'] + '\n')
                        answer = re.sub('<[^<]+?>', '', questions_array[counter]['answer'])
                        states.append(str(counter) + '_asked')
                    else:
                        states.append('game_over')
                        query = input('Game over! Right answer was: ' + answer + '\nYour score is ' + str(score) + ' out of ' + str(questions_number) + '\nIf you want to play again just type "repeat"\n')
        elif re.match(play_pattern, query, re.IGNORECASE):
            query = input('Let\'s play! How many questions you\'d like me to ask? (1-100)\n')
        else:
            states.append('no_match')
            query = input('For now I don\'t know how to handle this! Go & play with me\n')

chatbot()

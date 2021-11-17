import PySimpleGUI as sg
from re import sub
import tkinter as tk
from tkinter import *
from tkinter import font
from types import WrapperDescriptorType
from PIL.ImageColor import colormap
from PySimpleGUI.PySimpleGUI import WIN_CLOSED
from bs4.element import ContentMetaAttributeValue, whitespace_re
import moviepy
from moviepy.editor import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, VideoFileClip
from moviepy.editor import *
import textwrap

from PIL import Image, ImageFont, ImageDraw

import json
import pyttsx3
import os
import random


import markdown  # pip install markdown
from bs4 import BeautifulSoup  # pip install beautifulsoup4

import praw
from praw.models import MoreComments


# HELPER FUNCTIONS
def get_post(auth, post_id="", get_body=False):
    reddit = auth
    data = []

    if post_id:
        submission = reddit.submission(post_id)
        if get_body:
            data.append({
                'title': submission.title,
                'body': submission.selftext,
                'author': submission.author,
                'ups': submission.ups,
                'id': submission.id
            })
        else:
            data.append({
                'title': submission.title,
                'author': submission.author,
                'ups': submission.ups,
                'id': submission.id
            })
    else:
        pass
    """
        else:
        for submission in reddit.subreddit(subreddit).hot(limit=25):
            if get_body:
                data.append({
                    'title': submission.title,
                    'body': submission.selftext,
                    'author': submission.author,
                    'ups': submission.ups,
                    'id': submission.id
                })
            else:
                data.append({
                    'title': submission.title,
                    'author': submission.author,
                    'ups': submission.ups,
                    'id': submission.id
                })

    """
    return data


def get_comment(auth, post_id):
    reddit = auth
    data = []

    submission = reddit.submission(id=post_id)
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue

        data.append({
            'body': top_level_comment.body,
            'author': top_level_comment.author,
            'ups': top_level_comment.ups
        })
    return data


def get_title_by_id(auth, post_id):
    reddit = auth
    data = []
    submission = reddit.submission(id=post_id)
    return submission.title


def concatenate_video_moviepy(videos, out):
    clips = [VideoFileClip(c) for c in videos]
    final_clip = moviepy.editor.concatenate_videoclips(clips)
    final_clip.write_videofile(out)


def check_folders():
    if os.path.isdir('temp/') and os.path.isdir('images/'):
        pass
    else:
        try:
            os.mkdir('temp')
            os.mkdir('images')
        except FileExistsError:
            pass


def create_image(text, output_path, backdrop='wp.jpg', font=30, Xcord=100, Ycord=100, color=(237, 230, 211)):
    base = Image.open(f'assets/{backdrop}')
    font = ImageFont.truetype('assets/font.ttf', font)
    base_edit = ImageDraw.Draw(base)
    base_edit.text((Xcord, Ycord), text, color, font=font)
    base.save(output_path)


def create_video_from_audio(audio_path, image_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(output_path)


def wrap_text(unwrapped_text, width=80):
    wp = textwrap.TextWrapper(width=width)
    word_list = wp.wrap(unwrapped_text)
    return word_list
    # wrapped_text = ""
    # for g in word_list[:-1]:
    #     wrapped_text = wrapped_text + g + '\n'
    # wrapped_text += word_list[-1]
    # return wrapped_text


filter_list = {
    'fuck': 'frick',
    'fucking': 'fricking',
    'bitch': 'female dog',
    'shit': 'poop',
}


def filter_nsfw(sentence, filter_list):
    nsfw_list = list(filter_list.keys())
    words = [i for i in (sentence.lower()).split(' ')]
    result = ""
    for word in words:
        if word in nsfw_list:
            result += filter_list[word] + ' '
        else:
            result += word + ' '
    return result


# https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
def md_to_text(md):
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, features='html.parser')
    return soup.get_text()


# MAIN

def auth(client_id, client_secret, username, password):
    return praw.Reddit(
        user_agent="Comment Extraction (by u/USERNAME)",
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
    )


def make_mp4_posts(auth,  post_id, backdrop='wp.jpg', filter_list=filter_list, output='final.mp4', Xcord=100, Ycord=100, color=(255, 255, 255)):
    """
    A functions which created post videos; Taking a long post and slicing it into different frams; putting it all together in one video

    - auth: a praw auth object
    - post_id: id of the post
    - backdrop: looks for the backdrop image in assets/
    - output: output file path with name
    - Xcord, Ycord: specifies where the text should be located in the string.
    - color: Color in the rgb format as a tuple
    """
    post = get_post(auth, post_id, get_body=True)[0]
    body = post['body']
    post_author = post['author']

    check_folders()
    base_image_path = 'images'
    base_temp_path = 'temp'
    base_assets_path = 'assets'

    video_clips = []
    engine = pyttsx3.init()
    title = get_title_by_id(a, post_id)

    # Save the title image
    wrapped_title = f"posted by user {post_author} \n"
    for words in wrap_text(title, width=90):
        wrapped_title += words + '\n'

    # Save the title
    engine.save_to_file(wrapped_title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    create_image(wrapped_title, f'{base_image_path}/0.jpg', backdrop=backdrop,
                 Xcord=Xcord, Ycord=Ycord, color=color)

    create_video_from_audio(
        f'{base_temp_path}/0.mp3', f'{base_image_path}/0.jpg', f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')

    # Create text which is broken down
    unwrapped_text = md_to_text(filter_nsfw(body, filter_list))

    # Breaks down long texts into paras with width 1200, then its breaks down those pars into short sentences
    # FONT - VERDANA
    # SIZE - 35
    # Main text width (defines how long text in the picture will be) = 2000
    # Sentence width (definines how wide sentences will be) = 110
    wrapped_text = wrap_text(unwrapped_text, width=2200)
    i = 1
    for paragraphs in wrapped_text:
        paragraphs = wrap_text(f'{paragraphs}', width=110)
        st = ""
        for sentences in paragraphs:
            st += sentences + '\n'

        engine.save_to_file(st, f'{base_temp_path}/{i}.mp3')
        engine.runAndWait()

        create_image(st, f'{base_image_path}/{i}.jpg', backdrop=backdrop,
                     Xcord=Xcord, Ycord=Ycord, color=color)

        create_video_from_audio(
            f'{base_temp_path}/{i}.mp3', f'{base_image_path}/{i}.jpg', f'{base_temp_path}/{i}.mp4')

        video_clips.append(f'{base_temp_path}/{i}.mp4')
        os.remove(f'{base_temp_path}/{i}.mp3')

        i += 1
    concatenate_video_moviepy(video_clips, output)


def make_mp4_comments(auth, post_id, backdrop='wp.jpg', output='final.mp4', number_of_comments=10, filter_list=filter_list, font=30, Xcord=100, Ycord=100, color=(237, 230, 211)):
    """
    A function which creates a video from jpg and audio files of reddit posts with the id.

    - auth: a praw instance, can be created by passing in credentials to the auth function
    - post_id: The id of the post; example - qvcxdt
    - backdrop: Looks for the image in assets/
    - output: path (with name) of the output file
    - number_of_comments: Number of comments to be scraped
    - font: Font size
    - Xcord, Ycord: Define the position of the text on the image
    - color: Color of the text
    """
    check_folders()
    base_image_path = 'images'
    base_temp_path = 'temp'
    base_assets_path = 'assets'
    number_of_comments += 1
    backdrop_image = f'{base_assets_path}/{backdrop}'

    video_clips = []
    engine = pyttsx3.init()
    title = get_title_by_id(a, post_id)

    # Save the title
    engine.save_to_file(title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    # Save the title image
    #wrapped_title = f"posted by user {post_author} \n"
    wrapped_title = ""
    for words in wrap_text(title, width=90):
        wrapped_title += words + '\n'

    create_image(wrapped_title, f'{base_image_path}/0.jpg', backdrop=backdrop,
                 Xcord=Xcord, Ycord=Ycord, color=color, font=font)

    audio_clip = AudioFileClip(f'{base_temp_path}/0.mp3')
    image_clip = ImageClip(f'{base_image_path}/0.jpg')
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')

    comments = get_comment(auth, post_id)

    i = 1
    while i < number_of_comments:
        try:
            comment = comments[i]
        except IndexError:
            print(f'Only {i} comments were found; stopping.')
            concatenate_video_moviepy(video_clips, output)
            break

        filtered_text = filter_nsfw(comment['body'], filter_list)

        # Saves mp3 of the comment to a file
        engine.save_to_file(filtered_text, f'temp/{i}.mp3')
        engine.runAndWait()

        # Create text which is broken down
        # base = Image.open(backdrop_image)
        unwrapped_text = filtered_text
        wp = textwrap.TextWrapper(width=100)
        word_list = wp.wrap(unwrapped_text)
        wrapped_text = ""
        for g in word_list[:-1]:
            wrapped_text = wrapped_text + g + '\n'
        wrapped_text += word_list[-1]

        wrapped_text = md_to_text(wrapped_text)

        # Save a jpg of the text
        create_image(wrapped_text, f'{base_image_path}/{i}.jpg', backdrop=backdrop,
                     Xcord=Xcord, Ycord=Ycord, color=color, font=font)

        # Combine image and audio
        audio_clip = AudioFileClip(f'{base_temp_path}/{i}.mp3')
        image_clip = ImageClip(f'{base_image_path}/{i}.jpg')
        video_clip = image_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration
        video_clip.fps = 1
        video_clip.write_videofile(f'{base_temp_path}/{i}.mp4')
        video_clips.append(f'{base_temp_path}/{i}.mp4')
        os.remove(f'{base_temp_path}/{i}.mp3')

        i += 1

    concatenate_video_moviepy(video_clips, output)


try:
    with open('credentials.json') as file:
        data = json.loads(file.read())
except:
    print('The file wasnt found; or the credentials werent in the correct format')

user_agent = data['user_agent']
client_id = data['client_id']
client_secret = data['client_secret']
username = data['username']
password = data['password']

a = auth(client_id, client_secret, username, password)
# Make comment video from the id
#make_mp4_comments(a, 'qugfow', number_of_comments=1, Xcord=50, Ycord=50)
# make_mp4_comments(
#    a, 'askreddit', 'qv7kun', number_of_comments=10,  backdrop='alternate2.jpg', Ycord=150)

"""
desktop = os.path.join(os.getcwd(), '..', 'output.mp4')
make_mp4_comments(a, 'qv7kun', backdrop='alternate1.jpg',
                  number_of_comments=10, output=desktop)

"""

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
text = ""
first_half = [
    [
        sg.In()
    ],
    [
        sg.Button('Get comments'),
        sg.Button('Get posts')
    ],
    [
        sg.Multiline(size=(90, 30), font=('Consolas', 9),
                     key='-NICE-', do_not_clear=False)
    ],
]


window = sg.Window('Window Title', first_half)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    number_of_comments = 5
    post_id = ''
    type = ''

    if event == 'Get comments':  # if user closes window or clicks cancel
        inp = list(window.read())[1]
        type = 'gc'
        if inp[0] != ' ':
            try:
                data = get_comment(a, inp[0])
                post_id = inp[0]
                for i in data:
                    window['-NICE-'].print(
                        f"author: {i['author']}\ncomment: {i['body']}\n\n")
            except:
                window['-NICE-'].print('Failure')

        else:
            pass

    elif event == 'Get posts':  # if user closes window or clicks cancel
        inp = list(window.read())[1]
        type = 'gp'
        if inp[0] != ' ':
            try:
                data = get_post(a, inp[0], get_body=True)
                print(data)
                post_id = inp[0]
                for i in data:
                    window['-NICE-'].print(
                        f"title: {i['title']}\npost: {i['body']}\n\n")
            except:
                window['-NICE-'].print('Failure')
        else:
            pass

    elif event == WIN_CLOSED:
        break


window.close()

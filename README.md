# Reddit text to speech generator

A python gui program to generate reddit text to speech videos from the id of any post.
**This project is complete as of now, feel free to suggest a feature or a bug via issues**

# Current functionality

- Generate videos for subs based on comments,(askreddit) so reading individual comments
- Generate videos for subs with longer posts,(entitledparents), so slicing the post into multiple frames to fit the text.
- Optional customizability options to change the font, backdrop, position of text on the screen

# Todo

- [x] Get comments based on the permalink
- [x] Generate mp3 and jpg of the post and its comments; concatenate both of them for a clip, them combine all the clip into one file
- [x] Migrate to praw
- [x] Ability to generate tts for post based subreddits (r/nosleep or r/relationships)
- Better post/comment formatting
  - [x] Nsfw filter
- Visual enhancements
  - [x] Slicing longer posts into to frames or jpg(s)
- Wrapping it all up into a nice ~~tkinter~~ pysimplegui window
  - [x] Implemented option for reading post or comments (with title)

# Usage

- Go to [reddit dev](https://ssl.reddit.com/prefs/apps/) to create a new app; Once the app is created copy the `client_id`, `client_secret`, `username` and reddit password to a file named `credentials.json`, the file should be in the following format -

```json
{
  "client_id": "SI8pN3DSbt0zor",
  "client_secret": "xaxkj7HNh8kwg8e5t4m6KvSrbTI",
  "username": "fakebot3",
  "password": "1guiwevlfo00esyy"
}
```

- do `pip install -r requirements.txt` to install all the dependencies and then, run `python main.py`

# Screenshots

<img src='screenshots/1.jpg' width=300px>
<img src='screenshots/2.jpg' width=300px >

# Backburners

- Converting links and emojis to plain text

# Hikari Ita (光板)

A flashcard app designed for Mark Nguyen to study Chinese and Japanese.

# How?

This section documents how to do certain things with the source.

## How do I setup and run locally?

You need python (2.7.10) and sqlite3 on your system.

```
$ virtualenv virtualenv
$ source virtualenv/bin/activate
$ pip install -r requirements.txt
$ FLASK_DEBUG=True FLASK_ENV=dev FLASK_APP=hikariita flask run
```

# Why?

This section documents why certain decisions were made.

## Why yet another flashcard app?

I tried Anki and found that the existing content on that platform to be hard to puruse.  Additionally, it only had a concept of "front" and "back".  Meaning you could only quiz on some pre-defined "front" and answer with some predefined "back".  Traditionally, it's Kanji in the front and meaning in the back.  I want something where I can quiz on any of the following and answer with the other two: (1) hirigana, (2) kanji, and (3) meaning.  Additionally, I found the Android app to be pretty janky and hard to understand.  Third, because the existing flashcard stacks were not exactly what I wanted, I needed a way of copying the content and adding what I desired, or fixing what was wrong.  Unfortunately, my only alternative was to upload my own content instead.

Given the amount of work I would need to put into creating this content, I figured adding the application layer on top to do exactly what I wanted was worth the time.

I should probably have tried a couple more apps until I was mostly dissatisfied.

## Why python?

I code in python mostly and I find it pretty easy to get something simple running quickly.  Basically all OS's come with it pre-packaged.

## Why sqlite?

Same as why python.

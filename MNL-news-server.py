import os

import json

import hashlib

import requests

import feedparser

from flask import Flask, request

from bs4 import BeautifulSoup

from openai import OpenAI

from MNL_news_sources import MNL_SOURCES
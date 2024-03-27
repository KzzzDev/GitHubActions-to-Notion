import requests
from bs4 import BeautifulSoup
import json
import os
import re

# APIトークンとデータベースID
BLOG_URL = os.environ.get("BLOG_URL")
BLOG_TAG = os.environ.get("BLOG_TAG")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DB_ID = os.environ.get("NOTION_DB_ID")

print(BLOG_TAG)

# タグをリストに変換
if BLOG_TAG:
  tags = BLOG_TAG.split('\n')
  print("Tags:", tags)
else:
  tags = []

# 各サービスのURLパターンを定義
qiita_url_pattern = r'^https?://qiita.com/'
zenn_url_pattern = r'^https?://zenn.dev/'
note_url_pattern = r'^https?://note.com/'
github_url_pattern = r'^https?://github.com/'
speakerdeck_url_pattern = r'^https?://speakerdeck.com/'

# 共有されたURLのサービスを判別し、アイコンを設定
if bool(re.match(qiita_url_pattern, BLOG_URL)):
  # URLがQiitaの場合はQiitaのアイコンを設定
  ICON_URL = ""
  tags.append("Qiita")
elif bool(re.match(zenn_url_pattern, BLOG_URL)):
  # URLがZennの場合はZennのアイコンを設定
  ICON_URL = ""
  tags.append("Zenn")
elif bool(re.match(note_url_pattern, BLOG_URL)):
  # URLがnoteの場合はnoteのアイコンを設定
  ICON_URL = ""
  tags.append("note")
elif bool(re.match(github_url_pattern, BLOG_URL)):
  # URLがGitHubの場合はGitHubのアイコンを設定
  ICON_URL = ""
  tags.append("GitHub")
elif bool(re.match(speakerdeck_url_pattern, BLOG_URL)):
  # URLがSpeaker Deckの場合はSpeaker Deckのアイコンを設定
  ICON_URL = ""
  tags.append("Speaker Deck")
else:
  # URLがその他の場合はデフォルトのアイコンを設定
  ICON_URL = "" 

if ICON_URL:
  ICON_PAYLOAD = {
    "type": "external",
    "external": {
      "url": ICON_URL
    }
  }
else:
  ICON_PAYLOAD = {
    "type": "emoji",
    "emoji": "🚀"
  }

# リクエストのヘッダー
headers = {
  'Authorization': f'Bearer {NOTION_API_KEY}',
  'Content-Type': 'application/json',
  'Notion-Version': '2021-05-13'  # 最新のバージョンを指定
}

def get_ogp_info(url):
    # URLからHTMLを取得
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    # OGP情報を取得
    ogp_data = {}
    ogp_tags = soup.find_all(lambda tag: tag.get('property', '').startswith('og:') or tag.get('name', '').startswith('og:'))
    for tag in ogp_tags:
        property_name = tag.get('property', tag.get('name'))[3:]  # 'og:'の部分を除去してキーとする
        ogp_data[property_name] = tag.get('content')

    return ogp_data

ogp_info = get_ogp_info(BLOG_URL)
BLOG_TITLE = ogp_info.get('title', '')
OG_IMAGE = ogp_info.get('image', '')

print("Title:", BLOG_TITLE)
print("URL:", BLOG_URL)
print("Image:", OG_IMAGE)

# データベースのプロパティを更新するリクエストの作成
payload = {
  "parent": {"database_id": NOTION_DB_ID},
  "properties": {
    "名前": {
      "title": [
        { "text": { "content": BLOG_TITLE } }
      ]
    },
    "URL": {
      "url": BLOG_URL
    }
  },
  "cover": {
      "type": "external",
      "external": {
          "url": OG_IMAGE
      }
  }
}


if tags:
  payload["properties"]["タグ"] = {
    "type": "multi_select",
    "multi_select": [{"name": tag} for tag in tags]
  }

payload["icon"] = ICON_PAYLOAD
print(payload)

# データベースのプロパティを更新するリクエストを送信
response = requests.post(f'https://api.notion.com/v1/pages',
                          headers=headers,
                          data=json.dumps(payload))

# レスポンスの確認
print(response.status_code)
print(response.json())

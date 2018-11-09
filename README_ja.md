# CodeScraper

## 概要
Github, Gitlab, Pastebinなどのサイトを事前に登録したキーワードで検索し、新しいものが見つかった際に通知してくれるSlackbotです

現在以下の機能が実装されています

|名前|説明|備考|
|---|---|---|
|github|Github の新規リポジトリを検索します||
|gist|Github Gist の新規投稿を検索します||
|github_code|Github のコード検索を行います<br>精度は Github のインデックスによります|github apiが必要です|
|gitlab|Gitlab の検索を行います||
|gitlab_snippet|Gitlab Snippetsの新規投稿のスクレイピングを行います|キーワードは正規表現で登録します<br>うまく動かない時があります|
|google_custom|Google Custom Search を用いて検索を行います|事前にサーチエンジンを作成し、そのEngine ID と API Token を設定する必要があります<br>無料版は1日100リクエストの制限があります|
|pastebin|Pastebin Scraping API を用いて Pastebin のスクレイピングを行います|利用には Pastebin PRO Account(有償)が必要です<br>キーワードは正規表現で登録します|

## Requirements
Docker を利用して、動かすことを想定しています

そうでない場合、Python3 及び以下のライブラリが必要です
 - slackbot (https://github.com/lins05/slackbot)
 - lxml
 - crontab

## インストール
Dockerを利用する場合

```sh
docker build -t codescraper .
```

Dockerを利用しない場合

```sh
pip3 install -r requirements
```

## 使い方
### CodeScrapterの起動
利用するには slackbot_settings.py が必要です
最初のこのファイルを作成してください

```sh
mv ./master/slackbot_settings.py.sample ./master/slackbot_settings.py
vim ./master/slackbot_settings.py
```

設定ファイルを編集します
- 必須項目
  - API_TOKEN (6行目)
    - Slackにログインしたうえで、 [ここ](https://my.slack.com/services/new/bot) にアクセスし、ボットを作成します
    - 作成したSlackボットのAPI Token を記載します
  - channels(17〜19行目)
    - Slackボットに通知させる Slackチャンネルを指定します
    - 上記で作成した Slackボット をここに記載するチャンネルに参加させておいてください
    - 最低でも1つ以上のチャンネルを記載しておく必要が有ります
  - Enable Targets(87〜94行目)
    - 有効化する検索ターゲットを選択してください(True|False)
    - 以下のターゲットを有効化するには別途設定が必要です
      - github_code : github_access_token の設定が必要です
      - pastebin : Pastebin PRO account(有償)と固定IPが必要です. 購入後、Pastebin に対してScraping API を利用する固定IPをホワイトリスト登録するように設定する必要があります
      - google_custom : google_custom_api_key と google_custom_search_engine_id の設定が必要になります
  - default_settings(23〜74行目)
    - 各検索ターゲットにキーワードを登録する際のデフォルトの設定です
    - 最低限 Channel を 自分の作成したチャンネルに変更してください
    - 各項目の内容は以下の表の通りです

|項目|説明|
|---|---|
|Enable|キーワードの有効無効を設定します(True&#124;False)|
|SearchLevel|検索ターゲット github, github_code における検索範囲の設定です(1&#124;2). 2より1のほうが広い範囲を検索します|
|Time_Range|検索ターゲット github, gist における検索範囲の日数を設定します. 検索実行日から、ここに設定された日数前以降に作成されたものが検索対象となります|
|Expire_date|キーワードの有効期限を設定します. 有効期限は登録時点に日にちから、ここに設定された日数後となります. 有効期限が切れたキーワードは自動で無効化されます|
|Exclude_list|通知除外リストです. スクリプトが自動で書き換えるため、この設定は不要です.|
|Channel|通知するチャンネルを設定します. 上記の channels で設定したチャンネルを1つ記載してください|

- 任意設定
  - github_access_token(78行目)
    - github_code を有効にした場合必要です
    - [ここ](https://github.com/settings/tokens) から取得してください
  - google_custom_api_key(83行目)
    - google_custom を有効にした場合必要です
    - [ここ](https://console.developers.google.com/) から取得してください
  - google_custom_search_engine_id
    - google_custom を有効にした場合必要です
    - [ここ](https://console.developers.google.com/) から取得してください
  - Interval(97〜106行目)
    - 各検索ターゲットの検索実行時間を設定します
    - crontab の形式で記載します

設定ファイルを作成し、そのファイルを共有して Dockerコンテナを実行します

```sh
docker run -d --name codescraper -v $PWD/master/slackbot_settings.py:/home/codescraper/master/slackbot_settings.py codescraper
```

起動に成功すると、 Slcak に 以下のような通知が来ます
> ---CodeScraper Slackbot Started---
>
> github : SUCCESS : Started <br>
> gist : SUCCESS : Started <br>
> gitlab : SUCCESS : Started <br>

### CodeScraper コマンド
検索のキーワードは Slackボット を通じたコマンドによって操作します

はじめに、Slackボットに対して、以下のコマンドを送ると、コマンドのヘルプを表示します

```
@{Slackbotの名前} help:
```

```
Command Format is Following:
    {Command}: {target}; {arg1}; {arg2}; ...

Command List:

'setKeyword: target; [word]'    Add [word] as New Search Keyword with Default Settings.
(abbreviation=setK:)
'enableKeyword: target; [index]'    Enable the Search Keyword indicated by [index].
(abbreviation=enableK:)
'disableKeyword: target; [index]'    Disable the Search Keyword indicated by [index].
(abbreviation=disableK:)
'setSearchLevel: target; [index]'    Set Search Level of Github Search (1:easily 2:) indicated by [index]. It is used in github and github_code.
(abbreviation=setSL:)
'setExpireDate: target; [index]; [expiration date]'    Set a Expiration Date of the Keyword indicated by [index]. [expiration date] Format is YYYY-mm-dd.
(abbreviation=setED:)
'setChannel: target; [index];[channel]'    Set channel to notify the Search Keyword's result.
(abbreviation=setC:)
'getKeyword: target;'    Listing Enabled Search Keywords.
(abbreviation=getK:)
'getAllKeyword: target;'    Listing All Search Keyword (include Disabled Keywords).
(abbreviation=getAllK:)
'getSearchSetting: target; [index]'    Show Setting of the Search Keyword indicated by [index].
(abbreviation=getSS:)
'help:'    Show this Message.

Target:
    github
    gist
    github_code
    gitlab
    gitlab_snippet (Use RE match)
    google_custom
    pastebin (Use RE match)
```

Slackボットに対してコマンドを送ることで、キーワードを登録していきます

コマンドの以下の通りです.
具体的な利用方法は help: コマンドを参照してください

|コマンド名|説明|有効な検索ターゲット|
|---|---|---|
|setKeyword:|新しいキーワードを登録します|すべて|
|enableKeyword:|指定したキーワードを有効化します|すべて|
|disableKeyword:|指定したキーワードを無効化します|すべて|
|setSearchLevel:|指定したキーワードの検索範囲を設定します|github, github_code|
|setExpireDate:|指定したキーワードの有効期限を設定します|すべて|
|setChannel:|指定したキーワードを通知するSlackチャンネルを指定します|すべて|
|getKeyword:|設定されている検索キーワードのうち有効化されているものの一覧を表示します|すべて|
|getAllKeyword:|設定されている検索キーワードの一覧を表示します|すべて|
|getSearchSetting:|指定したキーワードの現在の設定を表示します|すべて|
|help:|ヘルプを表示します|-|

登録されたキーワードには Index が振られます。設定の変更には Index を指定します。
各キーワードの Index はキーワードの登録時、もしくは getKeyword: コマンドによって知ることができます。

![CodeScraper-1](img/codescraper-1.png)

Github 新しいリポジトリを見つけた際の通知

![CodeScraper-2](img/codescraper-2.png)

### 注意点
- Pastebin
  - Pastebin PRO Account（有償）が必要です
  - 購入後、[このページ](https://pastebin.com/doc_scraping_api) にて、CodeScraperを動かすホストのIPをホワイトリスト登録してください
  - ホワイトリスト登録が必要なため、固定IPが必要です
- Google Custom Search
  - 無料アカウントで利用できるリクエスト数には制限があり、1日100リクエストまでとなっています
  - 2時間おきに検索を行う設定とした場合、1日に12回検索を行います. 登録キーワードが9個を超えると、　12 * 9 = 108 となり、制限回数を超過します. 検索の頻度によって登録できるキーワードの数に制限があることを認識してください

## Author
[blueblue](https://twitter.com/piedpiper1616)

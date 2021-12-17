# Calendar from Stream
Add a stream schedule to google calendar

## What is this ?
Youtube(+etc...?)の配信予定をgoogleカレンダーに追加するやつ
~~(私の身内(?)で公開の要望が多ければ公開するわよ)~~
しません。Youtube Data APIのquotaがたりなさすぎて私一人で精一杯

## What does (framework, API, etc...) use ?
 - Docker Compose
 - Django
 - Postgresql
 - React(maybe)
 - Youtube Data API
 - Google Calendar API

## System diagram
こんな感じ 

<img src="https://user-images.githubusercontent.com/86540016/145006623-f4a4b6c8-c0c2-4682-b5d4-28f70b882cd7.png" width="100%"></img>

## 進捗どうですか？
だめです()

### Backend
 - チャンネルURLから配信予定リストの取得 <- ヨシ！！
 - Google アカウントの紐付け <- ヨシ！！
 - Google APIでカレンダーの権限取得 <- ヨシ！！
 - Google カレンダーに予定を追加 <- ヨシ！！
 - DBにアクセスしてユーザーごとに登録されたチャンネルURLの取得 <- ヨシ！！

***バックエンド完成！！（Beta）***

### Frontend
だめです(手を付けてない)

## Author
[twitter@yuto_o93](https://twitter.com/yuto_o93)

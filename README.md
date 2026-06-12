# kmoni-qt

[防災科研 強震モニタ](http://www.kmoni.bosai.go.jp/) の地図部分だけをコンパクトに表示する PyQt6 デスクトップアプリケーションです。

## 動作の仕組み

起動時にローカルホスト上で HTTP リバースプロキシを立ち上げ、`www.kmoni.bosai.go.jp` へのリクエストを中継します。HTML レスポンスには CSS を注入してヘッダー・フッター・各種コントロールを非表示にし、地図と凡例だけを表示します。WebEngine はこのローカルプロキシに接続するため、Same-Origin 制約を回避しつつ地震波の音声アラートも自動再生されます。

## 依存パッケージ

- Python 3
- PyQt6
- PyQt6-WebEngine
- requests

## インストール

```sh
make install
```

以下のファイルが配置されます。

| ファイル | インストール先 |
|---|---|
| `main.py` | `~/.local/bin/kmoni-qt` |
| `icon.svg` | `~/.local/share/icons/hicolor/scalable/apps/kmoni-qt.svg` |
| 生成された `.desktop` | `~/.local/share/applications/kmoni-qt.desktop` |

`.desktop` ファイルの `Exec=` にはインストール時の絶対パスが埋め込まれます。

## アンインストール

```sh
make uninstall
```

## 直接実行

```sh
python3 main.py
```

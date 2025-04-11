# memo-cli

タイムスタンプ付きでメモを保存できるCLIツール。  
`memo add` メモ、`memo list` で今日のメモを確認。

## install
```shell
git clone https://github.com/your-username/memo-cli.git
cd memo-cli
uv venv .venv
source .venv/bin/activate
uv pip install -e .

# シンボリックリンクを作成
ln -s "$(pwd)/.venv/bin/memo" ~/.local/bin/memo
```
pathが通っていない場合
```shell
export PATH="$HOME/.local/bin:$PATH"
```

## 初期設定
```shell
# memoを保存したいpathを .zshrc などに保存
export MEMO_DIR="$HOME/memo/daily"
```

## 使用例
### メモる

```
memo add 今から家を出る
```

- 保存先：`$MEMO_DIR/YYYY-MM-DD.md`
```
### memo
10:32 今から家を出る
```

### 確認

```
memo list
```

## 開発メモ
```
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```
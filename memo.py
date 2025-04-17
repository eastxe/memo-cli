import os
import click
from datetime import datetime
from pathlib import Path

HEADER = "### memo\n"  # セクション見出し
BLANK = "\n"  # 空行（可読性向上用）


def get_memo_dir() -> Path:
    """環境変数 MEMO_DIR からメモ保存先を取得（存在しなければエラー）"""
    memo_dir = os.environ.get("MEMO_DIR")
    if not memo_dir:
        raise click.UsageError(
            "❌ 環境変数 MEMO_DIR が設定されていません。例: export MEMO_DIR=~/memo/daily"
        )
    return Path(memo_dir).expanduser()


def get_today_memo_path(memo_dir: Path) -> Path:
    """今日の日付 (YYYY-MM-DD.md) をファイル名にした Path を返す"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return memo_dir / f"{date_str}.md"


@click.group()
def cli():
    """日々のメモを記録・表示する CLI ツール"""
    memo_dir = get_memo_dir()
    memo_dir.mkdir(parents=True, exist_ok=True)


@cli.command()
@click.argument("text", nargs=-1)
def add(text):
    """メモを追加する（例: memo add 朝ごはんを食べた）"""
    if not text:
        click.echo("⚠️  メモの内容が空です。")
        return

    memo_dir = get_memo_dir()
    memo_path = get_today_memo_path(memo_dir)
    now = datetime.now()

    # 新しく追記する 1 行
    entry = f"{now.strftime('%H:%M')} {' '.join(text)}\n"

    # 既存ファイル読み込み
    lines: list[str] = (
        memo_path.read_text(encoding="utf-8").splitlines(keepends=True)
        if memo_path.exists()
        else []
    )

    if HEADER in lines:
        # 既に ### memo がある → そのセクションの末尾を探す
        idx = lines.index(HEADER) + 1
        while idx < len(lines) and not lines[idx].startswith("#"):
            idx += 1
        lines.insert(idx, entry)  # 末尾（次のセクション直前）に挿入
    else:
        # まだ ### memo がない → 空行＋HEADER を挿入してからエントリーを追加
        if lines and lines[-1] != BLANK:  # 末尾が改行で終わっていなければ改行
            lines.append(BLANK)
        lines.extend([BLANK, HEADER, entry])  # 空行, HEADER, entry の順で追記

    # 保存
    memo_path.write_text("".join(lines), encoding="utf-8")
    click.echo(f"✅  メモを追加しました: {memo_path}")


@cli.command()
def list():
    """今日のメモを一覧表示"""
    memo_dir = get_memo_dir()
    memo_path = get_today_memo_path(memo_dir)

    if not memo_path.exists():
        click.echo("📭 今日のメモはまだありません。")
        return

    lines = memo_path.read_text(encoding="utf-8").splitlines()
    if HEADER.strip() not in (line.strip() for line in lines):
        click.echo("📭 今日の `### memo` セクションはまだありません。")
        return

    idx = next(i for i, line in enumerate(lines) if line.strip() == HEADER.strip()) + 1
    click.echo("📝 今日のメモ:")

    # 次の# で始まる任意のセクションが始まるまで
    while idx < len(lines) and not lines[idx].startswith("#"):
        line = lines[idx].strip()
        if line:
            click.echo(f"・{line}")
        idx += 1


if __name__ == "__main__":
    cli()

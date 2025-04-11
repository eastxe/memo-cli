import os
import click
from datetime import datetime
from pathlib import Path

def get_memo_dir() -> Path:
    memo_dir = os.environ.get("MEMO_DIR")
    if not memo_dir:
        raise click.UsageError("❌ 環境変数 MEMO_DIR が設定されていません。例: export MEMO_DIR=~/memo/daily")
    return Path(memo_dir).expanduser()

def get_today_memo_path(memo_dir: Path) -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return memo_dir / f"{date_str}.md"

@click.group()
def cli():
    """日々のメモを記録・表示するCLIツール"""
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
    time_str = now.strftime("%H:%M")
    entry = f"{time_str} {' '.join(text)}\n"
    header = "### memo\n"

    if memo_path.exists():
        with memo_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []

    if header in lines:
        idx = lines.index(header) + 1
        while idx < len(lines) and not lines[idx].startswith("###"):
            idx += 1
        lines.insert(idx, entry)
    else:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += [header, entry]

    with memo_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)

    click.echo(f"✅  メモを追加しました: {memo_path}")

@cli.command()
def list():
    """今日のメモを一覧表示"""
    memo_dir = get_memo_dir()
    memo_path = get_today_memo_path(memo_dir)

    if not memo_path.exists():
        click.echo("📭 今日のメモはまだありません。")
        return

    with memo_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    header = "### memo\n"
    if header not in lines:
        click.echo("📭 今日の `### memo` セクションはまだありません。")
        return

    idx = lines.index(header) + 1
    click.echo("📝 今日のメモ:")
    while idx < len(lines) and not lines[idx].startswith("###"):
        line = lines[idx].strip()
        if line:
            click.echo(f"・{line}")
        idx += 1

if __name__ == "__main__":
    cli()

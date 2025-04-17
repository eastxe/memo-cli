import os
import click
from datetime import datetime
from pathlib import Path

HEADER = "### memo\n"  # メモ用セクション見出し
BLANK = "\n"  # 空行


# ----------------------------------------------------------------------
# ヘルパ
# ----------------------------------------------------------------------
def get_memo_dir() -> Path:
    memo_dir = os.environ.get("MEMO_DIR")
    if not memo_dir:
        raise click.UsageError(
            "❌ MEMO_DIR が未設定です。例: export MEMO_DIR=~/memo/daily"
        )
    return Path(memo_dir).expanduser()


def today_memo_path() -> Path:
    return get_memo_dir() / f"{datetime.now():%Y-%m-%d}.md"


# ----------------------------------------------------------------------
@click.group()
def cli():
    """日々のメモを記録・表示する CLI ツール"""
    get_memo_dir().mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------
# `memo add`
# ----------------------------------------------------------------------
@cli.command()
@click.argument("text", nargs=-1)
def add(text: tuple[str]):
    """メモを追加する（例: memo add 朝ごはんを食べた）"""
    if not text:
        click.echo("⚠️  メモの内容が空です。")
        return

    memo_path = today_memo_path()
    new_entry = f"{datetime.now():%H:%M} {' '.join(text)}\n"

    # 既存内容
    lines: list[str] = (
        memo_path.read_text(encoding="utf-8").splitlines(keepends=True)
        if memo_path.exists()
        else []
    )

    # --------------------------------------------------
    # 1) HEADER が既にある場合
    # --------------------------------------------------
    if HEADER in lines:
        header_idx = lines.index(HEADER)

        # 「次のセクション」開始位置を探す
        next_hdr_idx = header_idx + 1
        while next_hdr_idx < len(lines) and not lines[next_hdr_idx].startswith("#"):
            next_hdr_idx += 1

        # メモセクションの末尾（最後の実エントリ）の直後を算出
        last_entry_idx = next_hdr_idx - 1
        while last_entry_idx > header_idx and lines[last_entry_idx].strip() == "":
            last_entry_idx -= 1

        insert_idx = last_entry_idx + 1  # = 末尾直後
        lines.insert(insert_idx, new_entry)  # 追記（時系列＝古→新）

        # -------------- 空行をちょうど 1 行に整形 --------------
        # 再度「次のセクション」開始位置を取り直し
        next_hdr_idx = insert_idx + 1
        while next_hdr_idx < len(lines) and not lines[next_hdr_idx].startswith("#"):
            next_hdr_idx += 1

        # 既存の空行を全削除
        del lines[insert_idx + 1 : next_hdr_idx]

        # 次のセクションがある場合だけ 1 行の空行を入れる
        if next_hdr_idx < len(lines):
            lines.insert(insert_idx + 1, BLANK)

    # --------------------------------------------------
    # 2) HEADER が無い場合
    #    - ファイル先頭なら空行を入れず HEADER を置く
    #    - 途中なら HEADER の前に 1 行の空行
    # --------------------------------------------------
    else:
        if lines:  # 既存内容がある（先頭ではない）
            if not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            if lines[-1] != BLANK:  # 末尾が空行でなければ 1 行追加
                lines.append(BLANK)
        lines.extend([HEADER, new_entry])

    # 保存
    memo_path.write_text("".join(lines), encoding="utf-8")
    click.echo(f"✅  メモを追加しました: {memo_path}")


# ----------------------------------------------------------------------
# `memo list`
# ----------------------------------------------------------------------
@cli.command()
def list():
    """今日のメモを一覧表示（時系列順）"""
    memo_path = today_memo_path()

    if not memo_path.exists():
        click.echo("📭 今日のメモはまだありません。")
        return

    lines = memo_path.read_text(encoding="utf-8").splitlines()
    try:
        idx = next(i for i, ln in enumerate(lines) if ln.strip() == HEADER.strip()) + 1
    except StopIteration:
        click.echo("📭 今日の `### memo` セクションはまだありません。")
        return

    click.echo("📝 今日のメモ:")
    while idx < len(lines) and not lines[idx].startswith("#"):
        if lines[idx].strip():
            click.echo(f"・{lines[idx].strip()}")
        idx += 1


# ----------------------------------------------------------------------
if __name__ == "__main__":
    cli()

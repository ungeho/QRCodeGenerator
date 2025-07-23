import os
import subprocess
import shutil
from datetime import datetime
import math



# --- ユーザーにレイアウト設定を選ばせる ---
print("画像の配置方法を選んでください：")
print("1: 自動カラム調整")
print("2: 画像サイズを指定（単位：cm）")

while True:
    mode = input("選択（1または2）: ").strip()
    if mode in {"1", "2"}:
        break
    print("無効な入力です。1 または 2 を入力してください。")

use_fixed_size = (mode == "2")

if use_fixed_size:
    while True:
        try:
            fixed_width_cm = float(input("画像の幅（cm）: "))
            fixed_height_cm = float(input("画像の高さ（cm）: "))
            break
        except ValueError:
            print("数値で入力してください。")
else:
    fixed_width_cm = None
    fixed_height_cm = None

# --- 設定 ---
image_dir = "qrcodes"
output_dir = "latex"
pdf_dir = "pdf"
tex_filename = "qrcode_images.tex"
pdf_filename = "qrcode_images.pdf"
max_columns = 4
images_per_page = 12

# latex フォルダを削除（存在する場合のみ）
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
    print(f"一時フォルダ'{output_dir}'を削除しました。")



# --- LaTeX用に特殊文字を安全に変換（_ と % は削除） ---
def escape_latex_caption(text):
    remove_chars = ["_", "%"]
    replacements = {
        "&": r"\&",
        "$": r"\$",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": "",  # バックスラッシュ削除（TeX Live 2016対応）
    }
    for char in remove_chars:
        text = text.replace(char, "")
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

# --- qrcodes フォルダの存在確認 ---
if not os.path.exists(image_dir):
    print(f"画像フォルダ '{image_dir}' が見つかりません。")
    exit()

# --- 画像ファイル一覧取得 ---
image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(".png")])
if not image_files:
    print(f"'{image_dir}' フォルダに PNG 画像が見つかりません。")
    exit()

# --- 出力ディレクトリの準備 ---
os.makedirs(output_dir, exist_ok=True)

# --- latex フォルダに画像をコピー ---
for filename in image_files:
    shutil.copyfile(os.path.join(image_dir, filename), os.path.join(output_dir, filename))

# --- 日付付きタイトル生成 ---
today_str = datetime.now().strftime("%Y年%m月%d日")
title = f"QRコード一覧（{today_str}）"

# --- LaTeXソースの構築 ---
latex_lines = [
    r"\documentclass{article}",
    r"\usepackage{graphicx}",
    r"\usepackage{subcaption}",
    r"\usepackage[a4paper, margin=1in]{geometry}",
    r"\usepackage{titlesec}",
    r"\usepackage{caption}",
    r"\captionsetup[subfigure]{labelformat=empty}",
    r"\title{" + escape_latex_caption(title) + r"}",
    r"\date{}",
    r"\begin{document}",
    r"\maketitle"
]

# --- ページごとに画像を配置 ---
total_images = len(image_files)
pages = math.ceil(total_images / images_per_page)

for page in range(pages):
    start = page * images_per_page
    end = min(start + images_per_page, total_images)
    batch = image_files[start:end]

    columns = min(len(batch), max_columns)
    width = 1 / columns

    latex_lines.append(r"\begin{figure}[htbp]")
    latex_lines.append(r"\centering")

    for i, filename in enumerate(batch):
        escaped_name = escape_latex_caption(filename)
        latex_lines.append(f"  \\begin{{subfigure}}[b]{{{width:.2f}\\textwidth}}")
        latex_lines.append(f"    \\centering")
        if use_fixed_size:
            latex_lines.append(f"    \\includegraphics[width={fixed_width_cm}cm,height={fixed_height_cm}cm,keepaspectratio]{{{filename}}}")
        else:
            latex_lines.append(f"    \\includegraphics[width=\\textwidth]{{{filename}}}")
        latex_lines.append(f"    \\caption{{{escaped_name}}}")
        latex_lines.append(f"  \\end{{subfigure}}")

        if (i + 1) % columns == 0:
            latex_lines.append("  \\vspace{0.5cm}\\par")

    latex_lines.append(r"\end{figure}")
    latex_lines.append(r"\clearpage")

latex_lines.append(r"\end{document}")

# --- .tex ファイルに保存 ---
tex_path = os.path.join(output_dir, tex_filename)
with open(tex_path, "w", encoding="utf-8") as f:
    f.write("\n".join(latex_lines))

print(f"LaTeXソースを '{tex_path}' に保存しました。")

# --- PDF 生成（pdflatex 実行） ---
try:
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_filename],
        cwd=output_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("LaTeXのコンパイルに失敗しました。")
        print("----- STDERR -----")
        print(result.stderr)
    else:
        print(f"PDFファイル '{os.path.join(output_dir, pdf_filename)}' を生成しました。")

        # 中間ファイル削除
        for ext in [".aux", ".log", ".out", ".toc"]:
            temp_path = os.path.join(output_dir, tex_filename.replace(".tex", ext))
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # PDF を pdf フォルダに移動
        os.makedirs(pdf_dir, exist_ok=True)
        src_pdf = os.path.join(output_dir, pdf_filename)
        dst_pdf = os.path.join(pdf_dir, pdf_filename)
        shutil.move(src_pdf, dst_pdf)
        print(f"PDFファイルを '{dst_pdf}' に移動しました。")

        # latex フォルダを削除
        # shutil.rmtree(output_dir)
        # print(f"一時フォルダ '{output_dir}' を削除しました。")

except FileNotFoundError:
    print("pdflatex が見つかりません。TeX Live または MiKTeX のインストールとパス設定を確認してください。")
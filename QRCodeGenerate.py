import qrcode
import os
from datetime import datetime

# --- 入力受付 ---
data = input("QRコードにしたい文字列を入力してください: ")

print("誤り訂正レベルを選択してください：")
print("L: 約7%復元可能（最低）")
print("M: 約15%復元可能")
print("Q: 約25%復元可能")
print("H: 約30%復元可能（最高）")
level = input("誤り訂正レベルを入力してください（L/M/Q/H）: ").upper()

filename_base = input("保存する画像ファイル名を入力してください（拡張子不要）: ")
ext = ".png"

# --- フォルダの設定と作成 ---
save_dir = "qrcodes"
os.makedirs(save_dir, exist_ok=True)

# --- 誤り訂正レベルのマッピング ---
error_correction_dict = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

# --- 入力チェック ---
if level not in error_correction_dict:
    print("無効な誤り訂正レベルが指定されました。L/M/Q/Hのいずれかを入力してください。")
    exit()

# --- 重複を避けるファイル名生成（YYYYMMDD付き） ---
def get_unique_filename(base, directory, ext):
    date_str = datetime.now().strftime("%Y%m%d")
    counter = 0
    while True:
        if counter == 0:
            filename = f"{base}_{date_str}{ext}"
        else:
            filename = f"{base}_{date_str}_{counter}{ext}"
        full_path = os.path.join(directory, filename)
        if not os.path.exists(full_path):
            return full_path
        counter += 1

save_path = get_unique_filename(filename_base, save_dir, ext)

# --- QRコード生成 ---
qr = qrcode.QRCode(
    version=1,
    error_correction=error_correction_dict[level],
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# --- 画像保存 ---
img = qr.make_image(fill_color="black", back_color="white")
img.save(save_path)

print(f"QRコードを '{save_path}' に保存しました。")

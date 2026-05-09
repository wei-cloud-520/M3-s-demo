import os

src = "/data/kaltsit_zh/kaltsit.list"
dst = "/workspace/logs/kaltsit/2-name2text.txt"

os.makedirs("/workspace/logs/kaltsit", exist_ok=True)

with open(src, "r", encoding="utf-8") as f:
    with open(dst, "w", encoding="utf-8") as g:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 4:
                # Already has 4 columns: path|speaker|lang|text
                g.write(line.strip() + "\n")
            elif len(parts) == 3:
                # 3 columns: path|speaker|text, add zh
                g.write(parts[0] + "|" + parts[1] + "|zh|" + parts[2] + "\n")

count = sum(1 for _ in open(dst, encoding="utf-8"))
print(f"Done: {count} entries written to {dst}")

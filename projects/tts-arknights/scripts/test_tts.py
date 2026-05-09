from gradio_client import Client

c = Client('http://127.0.0.1:9872')
result = c.predict(
    '/data/kaltsit_zh/char_003_kalts_boc#6_CN_001.wav',
    '',
    'Chinese',
    '我会定期为你进行理学检查，记录你的生命征象与意识状态，其他人没有这个权限。任何人想对你进行进一步的检查，你都有权拒绝，明白吗？',
    'Chinese',
    '不切分',
    20, 0.6, 0.3,
    True,
    fn_index=3
)
print(result)

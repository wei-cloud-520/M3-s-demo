# 凯尔希 TTS 桌面应用需求书（完整版）

## 概述
一个Windows桌面应用，通过Docker容器内的GPT-SoVITS WebUI（Gradio）API合成语音，主要用途是**合成大段文本有声书**。最终打包为exe可执行文件。

## 环境信息
- Windows 11, Python 3.10.1
- Docker容器 `breakstring/gpt-sovits`，推理页面 `http://localhost:9872`
- 数据挂载目录: `E:\sound model\GPT-SoVITS-Train`
- 参考音频（容器内）: `/data/kaltsit_zh/char_003_kalts_boc#6_CN_001.wav`

## Gradio API 调用方式

### 推理 (fn_index=3)
```
POST http://localhost:9872/api/predict
Content-Type: application/json

{
  "data": [
    "/data/kaltsit_zh/char_003_kalts_boc#6_CN_001.wav",
    "",
    "Chinese",
    "博士，我们又见面了。",
    "Chinese",
    "凑四句一切",
    20, 0.6, 0.3,
    true
  ],
  "fn_index": 3
}
```
返回: `{"data": ["/tmp/gradio/xxxx/audio.wav"]}`

### 最佳参数
- GPT: `GPT_weights/kaltsit-e10.ckpt`
- SoVITS: `SoVITS_weights/kaltsit_e8_s1056.pth`
- top_k=20, top_p=0.6, temperature=0.3
- 无参考模式: true
- 切分: 短文本"不切分"，长文本"凑四句一切"

### Docker操作
- 获取容器ID: `docker ps --filter ancestor=breakstring/gpt-sovits --format {{.ID}}`
- 拷贝音频: `docker cp <容器ID>:<容器内路径> <本地路径>`

---

## 功能需求

### 1. 主界面
- **莱茵生命主题风格**：
  - 主色系：草绿（#6BBF59 / #7CCD7C）+ 橙色点缀（#F4A460）
  - 底色：深灰黑（#1A1A2E / #16213E）
  - 文字：白色/浅灰（#E0E0E0）
  - 整体风格：简洁线条、科技感、医疗实验室氛围、克制不花哨
  - 参考：莫比乌斯环元素、莱茵生命Logo的几何线条感
  - 圆角按钮、微阴影、扁平化设计
- 顶部：Docker容器连接状态指示（绿色=运行中，红色=未运行/启动中）
- 中间：文本输入区（支持多行大段文本）
- 下方：控制按钮区

### 1.5 容器生命周期管理（自动化）
- 应用启动时自动检测容器是否运行
- 未运行则自动启动（用以下命令）：
  ```
  docker run -d --gpus=all --env=is_half=False \
    -v "E:\sound model\GPT-SoVITS-Train:/data" \
    -v "E:\sound model\GPT-SoVITS-Train\output:/workspace/SoVITS_weights" \
    -v "E:\sound model\GPT-SoVITS-Train\logs:/workspace/logs" \
    -v "E:\sound model\GPT-SoVITS-Train\GPT_weights:/workspace/GPT_weights" \
    -p 9880:9880 -p 9871:9871 -p 9872:9872 -p 9873:9873 -p 9874:9874 \
    --shm-size="16G" \
    --name gpt-sovits-kaltsit \
    breakstring/gpt-sovits
  ```
- 用固定容器名 `gpt-sovits-kaltsit` 方便管理
- 启动后轮询等待WebUI就绪（检测9872端口可访问），显示"正在启动模型..."
- 应用退出时提示是否关闭容器，或提供设置项（退出自动关/保持运行）
- 容器已存在但未运行时自动 `docker start` 而不是重新 `docker run`

### 2. 文本输入
- 支持手动输入/粘贴
- 支持导入文件：txt、epub、pdf 等常见格式
- 导入后文本填入输入框，可编辑
- 支持拖拽文件到窗口

### 3. 参考音频选择
- 默认使用 `boc#6_CN_001`
- **预留**参考音频切换入口（下拉框或文件选择），界面先做但暂不要求功能完善
- 预留多说话人切换入口（为Mon3tr等其他角色模型做准备）

### 4. 切分模式
- 提供4种选项：自动 / 不切分 / 凑四句一切 / 凑50字一切
- "自动"根据文本长度判断（>100字用凑四句一切）

### 5. 输出格式
- 可选：wav / mp3
- mp3转换可用pydub+ffmpeg

### 6. 合成流程
1. 用户输入/导入文本 → 点"开始合成"
2. 大段文本自动切分为多个片段
3. 逐片段调用Gradio API合成
4. 每个片段的音频 docker cp 到本地临时目录
5. 所有片段合成完毕后，**自动拼接成一个完整音频文件**
6. 拼接可用pydub

### 7. 进度显示（重点）
- 进度条 + 文字提示
- 显示：当前第几句 / 总句数
- 显示：当前正在合成的文本内容
- 显示：已用时间 / 预估剩余时间
- 可视化，不能让用户干等

### 8. 播放
- 合成完成后可一键播放完整音频
- 也可播放单个片段（如果有列表的话）

### 9. 另存为
- 弹出文件选择对话框
- 文件名默认带时间戳

### 10. 存储管理
- 临时片段文件统一存到可配置的目录（默认 `E:\sound model\GPT-SoVITS-Train\output\tmp\`）
- 最终合并文件存到可配置的目录（默认 `E:\sound model\GPT-SoVITS-Train\output\`）
- **不自动清理**，由用户手动管理
- 在界面设置里可查看/打开存储目录

### 11. 错误处理
- 容器未运行：红色提示，引导启动
- API调用失败：显示具体错误
- 单个片段失败：记录错误，跳过继续，最后汇总报告
- 超时处理：单片段120秒超时

### 12. 打包
- 用 pyinstaller 打包成单个 exe
- 双击即用，不显示终端窗口
- exe和依赖（ffmpeg等）放同一目录

---

## 开发规范

### 环境管理
- 创建独立conda环境：`conda create -n kaltsit-tts python=3.10`
- 所有依赖装在这个环境里，不要装到base环境
- 激活环境后工作：`conda activate kaltsit-tts`
- 在项目README里记录环境创建步骤和依赖安装命令
- requirements.txt 记录所有依赖及版本

### 文件操作安全
- **工作区限定**：只能对工作区目录及其子目录进行读写操作
- 工作区路径：`E:\sound model\GPT-SoVITS-Train\kaltsit-tts\`
- 严禁修改/删除工作区外的任何文件
- Docker操作仅限容器名 `gpt-sovits-kaltsit`
- 输出文件仅写入配置的output目录

## 技术约束
- Python 3.10.1
- GUI: **PySide6**（Qt框架，支持QSS样式）
- HTTP: requests
- 音频拼接: pydub（需要ffmpeg）
- 格式转换: pydub
- 文件解析: epub用ebooklib，pdf用PyPDF2或pdfplumber
- **不要用 gradio_client**
- 用 pyinstaller 打包

## 容器启动命令（固定配置）
```powershell
docker run -d --gpus=all --env=is_half=False -v "E:\sound model\GPT-SoVITS-Train:/data" -v "E:\sound model\GPT-SoVITS-Train\output:/workspace/SoVITS_weights" -v "E:\sound model\GPT-SoVITS-Train\logs:/workspace/logs" -v "E:\sound model\GPT-SoVITS-Train\GPT_weights:/workspace/GPT_weights" -p 9880:9880 -p 9871:9871 -p 9872:9872 -p 9873:9873 -p 9874:9874 --shm-size="16G" --name gpt-sovits-kaltsit breakstring/gpt-sovits
```
注意: 用 `-d` 后台运行，不用 `-it`。容器名固定为 `gpt-sovits-kaltsit`。

## UI 设计规范

### 配色
- 背景: #1A1A2E（主背景）, #16213E（卡片/输入框）
- 主色: #6BBF59（草绿，按钮、进度条、状态指示）
- 辅色: #F4A460（橙色，强调/警告/点缀）
- 文字: #E0E0E0（主文字）, #888888（次要文字）
- 成功: #4ECCA3, 错误: #FF6B6B

### 风格
- 圆角: 8-12px
- 扁平化，微阴影
- 无多余装饰，信息密度适中
- 进度条使用草绿渐变
- 按钮hover有微变色效果

### 13. 智能停顿拼接
- 切分合成后，拼接时按标点类型插入静音间隔，模拟自然语速节奏
- 停顿分级（默认值，UI可调）：
  - 逗号、顿号、分号：0.3s
  - 句号、问号、叹号：0.6s
  - 段落换行：1.0s
- 界面提供停顿时长滑块/输入框，可统一缩放（倍率 0.5x ~ 2.0x）
- 实现方式：pydub 拼接时在片段间插入对应时长的 `silent` AudioSegment

### 14. 推理参数面板
- 将以下参数暴露到 UI，默认值沿用当前最优配置：
  - temperature：默认 0.3，范围 0.1 ~ 1.0，步进 0.05
  - top_k：默认 20，范围 1 ~ 100，步进 1
  - top_p：默认 0.6，范围 0.1 ~ 1.0，步进 0.05
- UI 形式：折叠面板或独立 Tab，展开后显示各参数滑块
- 每个参数旁显示当前值，支持手动输入精确数值
- 提供「恢复默认」按钮，一键重置所有参数
- 参数变更实时反映到下一次合成请求，无需重启

## 依赖列表

### 项目结构
```
kaltsit-tts/
├── main.py              # 入口
├── config.py            # 配置管理（容器命令、API地址、参数等）
├── models/              # 数据模型
│   ├── speaker.py       # 说话人配置（名字、参考音频、模型路径、参数）
│   └── tts_request.py    # TTS请求封装
├── services/            # 业务逻辑
│   ├── docker_manager.py # 容器生命周期管理
│   ├── tts_engine.py     # TTS引擎（Gradio API调用）
│   ├── audio_processor.py # 音频拼接、格式转换
│   └── file_parser.py    # 文件解析（txt/epub/pdf）
├── ui/                  # 界面
│   ├── main_window.py    # 主窗口
│   ├── components/       # 可复用组件
│   └── styles/           # QSS样式
│       └── theme.qss     # 莱茵生命主题
├── utils/               # 工具函数
└── README.md            # 项目文档
```

### 可扩展性要求
1. **换声音模型**：新增一个说话人只需在 `config.py` 里加一条配置（名字、参考音频、模型路径、参数），界面自动读取，不需要改其他代码
2. **换TTS引擎**：`tts_engine.py` 定义统一接口，换引擎（如从GPT-SoVITS换成其他）只需实现新引擎类，上层代码不动
3. **换UI框架**：UI层与业务逻辑完全分离，services/不依赖任何UI代码
4. **新增文件格式**：在 `file_parser.py` 里加解析器就行
5. **配置外置**：所有可变参数（容器路径、端口、模型路径、推理参数等）都在 `config.py` 或外部配置文件中，不硬编码

### 文档要求
- README.md：项目说明、安装步骤、使用方法
- 每个模块顶部有docstring说明职责
- 关键函数有注释说明参数和返回值
- config.py 里有详细的配置说明注释
```
PySide6
requests
pydub
ebooklib
PyPDF2
pyinstaller
```
注: ffmpeg 需要单独安装或打包

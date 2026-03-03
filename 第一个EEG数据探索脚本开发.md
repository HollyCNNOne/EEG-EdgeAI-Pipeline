# 第一个EEG数据探索脚本开发

## 一、核心思路

为彻底避开MNE官方示例数据集从国外服务器下载慢、路径匹配复杂的问题，我们直接用NumPy生成**带真实脑电生理特征**的模拟EEG信号，既保证数据的真实性，又100%可控，能快速验证环境和MNE库的基础操作。
模拟信号包含：

* **Alpha波（8-13Hz）**：模拟人闭眼放松时的核心脑电节律；
* **Beta波（14-30Hz）**：模拟人清醒/专注思考时的脑电特征；
* **生理背景噪声**：模拟真实脑电采集时的环境干扰，贴近实际场景。

## 二、完整可运行代码

将以下代码保存为 `scripts/01\_explore\_eeg.py`：

```python
import os
import numpy as np
import mne
import matplotlib.pyplot as plt

# ======================
# 1. 生成模拟EEG数据（无需下载任何外部文件）
# ======================
print("正在生成模拟EEG数据...")

# 标准EEG配置：32个通道、1000Hz采样率、30秒记录时长
n\_channels = 32
sfreq = 1000  # 采样频率：每秒采集1000个数据点
duration = 30  # 信号总时长（秒）
times = np.arange(0, duration, 1/sfreq)  # 生成时间轴

# 创建通道信息（符合EEG命名规范）
ch\_names = \[f'EEG{i+1:02d}' for i in range(n\_channels)]  # 通道名：EEG01~EEG32
ch\_types = \['eeg'] \* n\_channels  # 所有通道类型为EEG
info = mne.create\_info(ch\_names=ch\_names, sfreq=sfreq, ch\_types=ch\_types)

# 生成带真实脑电特征的信号（alpha波+beta波+背景噪声）
np.random.seed(42)  # 固定随机种子，结果可复现
data = np.zeros((n\_channels, len(times)))  # 初始化数据矩阵（通道数×时间点）
for i in range(n\_channels):
    alpha\_wave = 5e-6 \* np.sin(2 \* np.pi \* 10 \* times)  # 10Hz alpha波（核心特征）
    beta\_wave = 2e-6 \* np.sin(2 \* np.pi \* 20 \* times)   # 20Hz beta波（辅助特征）
    noise = np.random.randn(len(times)) \* 1e-6           # 生理背景噪声
    data\[i] = alpha\_wave + beta\_wave + noise  # 合成最终EEG信号

# 创建MNE标准Raw对象（MNE处理EEG数据的核心格式）
raw = mne.io.RawArray(data, info, verbose=False)
raw.set\_montage('standard\_1020', on\_missing='warn')  # 加载标准10-20电极位置

# ======================
# 2. 打印数据集核心信息
# ======================
print("\\n" + "="\*60)
print("📊 模拟EEG数据集基本信息")
print("="\*60)
print(f"采样频率：{raw.info\['sfreq']} Hz")
print(f"通道数量：{len(raw.ch\_names)}")
print(f"记录时长：{raw.times\[-1]:.2f} 秒")
print(f"通道名称：{raw.ch\_names\[:10]}...（仅显示前10个）")
print("="\*60)

# ======================
# 3. 绘制EEG波形图（修复窗口闪退问题）
# ======================
print("\\n正在绘制EEG波形图...")
fig = raw.plot(
    duration=10,        # 绘制前10秒的信号
    n\_channels=20,      # 显示前20个通道
    scalings=dict(eeg=20e-6),  # 固定EEG信号缩放比例，波形更清晰
    show=True,          # 显示绘图窗口
    block=True,         # 强制窗口保持，避免闪退
    title='EEG Raw Data (First 10s)'
)

# ======================
# 4. 保存文件到项目目录
# ======================
# 自动创建目录（避免路径不存在报错）
os.makedirs('notebooks', exist\_ok=True)
os.makedirs('data', exist\_ok=True)

# 保存波形图（300dpi高清）
output\_fig = os.path.join('notebooks', '01\_eeg\_waveform.png')
fig.savefig(output\_fig, dpi=300, bbox\_inches='tight')
print(f"\\n✅ 波形图已保存至：{output\_fig}")

# 保存EEG数据（MNE标准.fif格式，方便后续预处理）
output\_raw = os.path.join('data', 'simulated\_eeg\_raw.fif')
raw.save(output\_raw, overwrite=True)
print(f"✅ EEG数据已保存至：{output\_raw}")

# 终极防闪退：脚本暂停，按回车键才结束
print("\\n🎉 EEG探索脚本运行完成！波形窗口已保持，按回车键结束程序...")
input()
plt.show()
```

## 三、代码核心功能拆解

|代码模块|核心作用|
|-|-|
|模拟数据生成|无需依赖外部文件，直接生成符合真实生理特征的EEG信号，避开下载/路径问题|
|MNE Raw对象创建|将NumPy数组转为MNE标准格式，这是MNE处理EEG数据的基础|
|数据集信息打印|快速验证数据的核心参数（采样率、通道数、时长），确认数据生成正常|
|波形图绘制|可视化EEG信号，直观查看波形特征；`block=True` 解决窗口闪退问题|
|文件保存|将波形图和EEG数据保存到指定目录，为后续预处理提供数据基础|

## 四、常见问题与解决方案

|问题现象|核心原因|解决方法|
|-|-|-|
|波形窗口弹出后闪退|Python脚本执行完进程自动退出，窗口被关闭|代码中添加 `block=True`（绘图时）+ `input()`（脚本结尾）|
|VS Code中MNE标红色波浪线|VS Code的Python解释器选错（用了base环境，而非neuro环境）|按 `Ctrl+Shift+P` → 输入 `Python: Select Interpreter` → 选择带 `(neuro)` 的解释器|
|提示“文件路径不存在”|未创建notebooks/data目录，或代码中未自动创建|代码中添加 `os.makedirs('目录名', exist\_ok=True)`|
|执行脚本无输出/卡住|误使用base环境运行，未激活neuro环境|先执行 `conda activate neuro` 激活环境，再运行脚本|

## 五、运行验证

### 成功标志

1. 终端正常打印数据集信息，无报错；
2. 弹出EEG波形窗口，能清晰看到20个通道的波形，窗口不闪退；
3. `notebooks/` 目录下生成 `01\_eeg\_waveform.png`，`data/` 目录下生成 `simulated\_eeg\_raw.fif`。

---

### 手把手提交该脚本到GitHub的步骤

#### 第一步：确认文件已保存到正确位置

确保 `01\_explore\_eeg.py` 保存在项目根目录的 `scripts/` 文件夹下（路径：`D:\\GitHub\\EEG-EdgeAI-Pipeline\\scripts\\01\_explore\_eeg.py`）。

#### 第二步：打开Anaconda Prompt，执行以下命令

```bash
# 1. 切换到项目根目录
D:
cd GitHub\\EEG-EdgeAI-Pipeline

# 2. 激活neuro环境（可选，仅为确认环境）
conda activate neuro

# 3. 查看Git状态（确认新文件已识别）
git status

# 4. 添加脚本文件到Git暂存区
git add scripts/01\_explore\_eeg.py

# 5. 提交变更到本地仓库
git commit -m "feat: add first EEG exploration script with simulated data"

# 6. 推送到GitHub远程仓库
git push origin main
```

#### 第三步：验证提交结果

打开浏览器，刷新你的GitHub仓库页面，能在 `scripts/` 目录下看到 `01\_explore\_eeg.py` 文件，即提交成功。


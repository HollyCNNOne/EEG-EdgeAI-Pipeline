import os
import numpy as np
import mne
import matplotlib.pyplot as plt

# ======================
# 1. 生成带真实脑电特征的模拟EEG数据（无需下载任何文件）
# ======================
print("正在生成模拟EEG数据...")

# 标准EEG配置：32通道、1000Hz采样率、30秒时长
n_channels = 32
sfreq = 1000
duration = 30
times = np.arange(0, duration, 1/sfreq)

# 创建通道信息
ch_names = [f'EEG{i+1:02d}' for i in range(n_channels)]
ch_types = ['eeg'] * n_channels
info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)

# 生成带真实脑电节律的信号（alpha波+beta波+生理噪声）
np.random.seed(42)
data = np.zeros((n_channels, len(times)))
for i in range(n_channels):
    alpha = 5e-6 * np.sin(2 * np.pi * 10 * times)  # 10Hz alpha波（闭眼脑电特征）
    beta = 2e-6 * np.sin(2 * np.pi * 20 * times)   # 20Hz beta波（清醒脑电特征）
    noise = np.random.randn(len(times)) * 1e-6     # 背景噪声
    data[i] = alpha + beta + noise

# 生成MNE标准Raw对象
raw = mne.io.RawArray(data, info, verbose=False)
raw.set_montage('standard_1020', on_missing='warn')

# ======================
# 2. 打印数据集信息
# ======================
print("\n" + "="*60)
print("📊 EEG数据集基本信息")
print("="*60)
print(f"采样频率：{raw.info['sfreq']} Hz")
print(f"通道数量：{len(raw.ch_names)}")
print(f"记录时长：{raw.times[-1]:.2f} 秒")
print(f"通道名称：{raw.ch_names[:10]}...（仅显示前10个）")
print("="*60)

# ======================
# 3. 绘制EEG波形图（修复闪退）
# ======================
print("\n正在绘制EEG波形图...")
fig = raw.plot(
    duration=10,
    n_channels=20,
    scalings=dict(eeg=20e-6),
    show=True,
    block=True,  # 强制窗口保持，不会闪退
    title='EEG Raw Data (First 10s)'
)

# ======================
# 4. 保存文件
# ======================
os.makedirs('notebooks', exist_ok=True)
os.makedirs('data', exist_ok=True)

# 保存波形图
fig.savefig(os.path.join('notebooks', '01_eeg_waveform.png'), dpi=300, bbox_inches='tight')
# 保存EEG数据
raw.save(os.path.join('data', 'simulated_eeg_raw.fif'), overwrite=True)

# 防闪退：脚本暂停，按回车才会结束
print("\n✅ 波形图和EEG数据已保存完成！")
print("🎉 EEG探索脚本运行成功！波形窗口已保持，按回车键结束程序...")
input()
plt.show()
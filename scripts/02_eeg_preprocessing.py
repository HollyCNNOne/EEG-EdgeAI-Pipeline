import os
import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import detrend

# ======================
# 关键修正：切换工作目录到项目根目录
# ======================
# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 切换到项目根目录（脚本目录的父目录）
project_root = os.path.join(script_dir, '..')
os.chdir(project_root)
print(f"✅ 工作目录已切换到: {os.getcwd()}")

# 确保文件夹存在（现在是在项目根目录下创建）
os.makedirs('notebooks', exist_ok=True)
os.makedirs('data', exist_ok=True)

# ======================
# 1. 加载模拟EEG数据
# ======================
raw_path = os.path.join('data', 'simulated_eeg_raw.fif')
raw = mne.io.read_raw_fif(raw_path, preload=True, verbose=False)

print("原始数据信息：")
print(f"采样频率：{raw.info['sfreq']} Hz")
print(f"数据形状：{raw.get_data().shape} → (通道数, 时间点)")
print(f"原始信号范围：{np.min(raw.get_data()):.2e} ~ {np.max(raw.get_data()):.2e} V\n")

# ======================
# 2. 带通滤波（0.5~45Hz）
# ======================
raw.filter(l_freq=0.5, h_freq=45, fir_design='firwin', verbose=False)

# 验证滤波效果（功率谱对比）
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
raw_original = mne.io.read_raw_fif(raw_path, preload=True, verbose=False)
raw_original.compute_psd(fmax=60).plot(axes=ax1, show=False)
ax1.set_title('PSD Before Filtering (包含50Hz噪声)')
raw.compute_psd(fmax=60).plot(axes=ax2, show=False)
ax2.set_title('PSD After 0.5-45Hz Bandpass Filter (50Hz噪声已去除)')
plt.tight_layout()
fig.savefig(os.path.join('notebooks', '02_filtered_psd.png'), dpi=300, bbox_inches='tight')
plt.close(fig)
print("✅ 1/4 功率谱图已保存：notebooks/02_filtered_psd.png")

# ======================
# 3. ICA伪影去除（强制32个成分）
# ======================
raw_ica = raw.copy()
# 去趋势处理
data_detrended = detrend(raw_ica.get_data(), type='linear', axis=1)
raw_ica._data = data_detrended

# 训练ICA
ica = mne.preprocessing.ICA(
    n_components=32,
    random_state=42,
    max_iter=500,
    verbose=False
)
ica.fit(raw_ica)

# 剔除伪影成分
ica.exclude = [0, 1]
raw_clean = raw.copy()
ica.apply(raw_clean)

# --- 保存ICA前的信号图 ---
raw.plot(duration=5, n_channels=10, show=False, title='Before ICA (含伪影)')
fig1 = plt.gcf()
fig1.set_size_inches(12, 4)
fig1.savefig(os.path.join('notebooks', '02_before_ica.png'), dpi=300, bbox_inches='tight')
plt.close(fig1)
print("✅ 2/4 ICA前信号图已保存：notebooks/02_before_ica.png")

# --- 保存ICA后的信号图 ---
raw_clean.plot(duration=5, n_channels=10, show=False, title='After ICA (伪影已去除)')
fig2 = plt.gcf()
fig2.set_size_inches(12, 4)
fig2.savefig(os.path.join('notebooks', '02_after_ica.png'), dpi=300, bbox_inches='tight')
plt.close(fig2)
print("✅ 3/4 ICA后信号图已保存：notebooks/02_after_ica.png")

# ======================
# 4. 数据分段（Epoch）与基线校正
# ======================
sfreq = raw_clean.info['sfreq']
n_events = 10
events = np.array([[i * int(2 * sfreq), 0, 1] for i in range(n_events)])
event_id = {'eeg_segment': 1}

# 分段
epochs = mne.Epochs(
    raw_clean,
    events=events,
    event_id=event_id,
    tmin=-0.2,
    tmax=1.8,
    baseline=(-0.2, 0),
    preload=True,
    verbose=False
)

# --- 保存Epoch图 ---
epochs.plot(n_epochs=5, show=False, title='Epochs with Baseline Correction')
epochs_fig = plt.gcf()
epochs_fig.set_size_inches(12, 6)
epochs_fig.savefig(os.path.join('notebooks', '02_epochs.png'), dpi=300, bbox_inches='tight')
plt.close(epochs_fig)
print("✅ 4/4 Epoch分段图已保存：notebooks/02_epochs.png")

# ======================
# 5. 保存预处理后的数据
# ======================
raw_clean.save(os.path.join('data', 'eeg_clean_raw.fif'), overwrite=True)
epochs.save(os.path.join('data', 'eeg_epochs.fif'), overwrite=True)

# 最终验证：列出项目根目录下notebooks文件夹里的所有图片
print("\n📂 项目根目录 notebooks 文件夹中的图片文件：")
for file in os.listdir('notebooks'):
    if file.endswith('.png'):
        print(f"- {file}")

print(f"\n📊 预处理后数据统计：")
data_clean = epochs.get_data()
print(f"数据形状：{data_clean.shape}")
print(f"均值：{np.mean(data_clean):.2e} V")
print(f"标准差：{np.std(data_clean):.2e} V")

print("\n🎉 EEG信号预处理全流程完成！所有图片和数据都已保存到项目根目录。")
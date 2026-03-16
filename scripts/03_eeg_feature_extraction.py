import os
import mne
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 切换到项目根目录，保证路径绝对正确
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
os.chdir(project_root)
print(f"✅ 工作目录已切换到: {os.getcwd()}")

# 确保文件夹存在
os.makedirs('notebooks', exist_ok=True)
os.makedirs('features', exist_ok=True)

# ======================
# 1. 加载预处理好的Epoch数据
# ======================
epochs_path = os.path.join('data', 'eeg_epochs.fif')
epochs = mne.read_epochs(epochs_path, preload=True, verbose=False)

# 验证数据加载
print("✅ Epoch数据加载完成：")
print(f"数据形状：{epochs.get_data().shape} → (样本数, 通道数, 时间点)")
print(f"样本数：{len(epochs)} 个")
print(f"通道数：{len(epochs.ch_names)} 个")
print(f"采样率：{epochs.info['sfreq']} Hz\n")

# ======================
# 2. 定义脑电节律的频率范围（行业通用标准）
# ======================
frequency_bands = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 45)
}

# ======================
# 3. 计算功率谱密度（PSD）
# ======================
psd, freqs = epochs.compute_psd(
    fmin=0.5,
    fmax=45,
    method='welch',
    verbose=False
).get_data(return_freqs=True)

print("✅ PSD计算完成：")
print(f"PSD形状：{psd.shape} → (样本数, 通道数, 频率点数量)")
print(f"频率范围：{freqs.min():.1f} ~ {freqs.max():.1f} Hz\n")

# ======================
# 4. 计算每个节律的绝对功率和相对功率
# ======================
def calculate_band_power(psd, freqs, band):
    """计算单个节律的平均功率"""
    freq_mask = (freqs >= band[0]) & (freqs <= band[1])
    return np.mean(psd[..., freq_mask], axis=-1)

# 计算各节律绝对功率
band_powers = {}
total_power = np.zeros_like(psd[..., 0])  # 总功率，用于算相对占比
for band_name, band_range in frequency_bands.items():
    band_power = calculate_band_power(psd, freqs, band_range)
    band_powers[band_name] = band_power
    total_power += band_power

# 计算相对功率（核心特征，消除个体/设备差异）
relative_powers = {}
for band_name, band_power in band_powers.items():
    relative_powers[band_name] = band_power / total_power

# 打印结果，验证计算成功
print("✅ 节律功率计算完成：")
for band_name in frequency_bands.keys():
    mean_rel_power = np.mean(relative_powers[band_name]) * 100
    print(f"{band_name}波 平均相对功率：{mean_rel_power:.1f}%")

# ======================
# 5. 特征可视化（彻底修正cmap报错）
# ======================
# 计算全局平均相对功率
mean_rel_power = {
    band: np.mean(rel_power) * 100
    for band, rel_power in relative_powers.items()
}
bands_list = list(mean_rel_power.keys())
power_values = list(mean_rel_power.values())

# 提前生成颜色，彻底避免cmap参数报错
plot_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# 1. 绘制饼图
fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
ax_pie.pie(
    power_values,
    labels=bands_list,
    autopct='%1.1f%%',
    startangle=90,
    colors=plot_colors
)
ax_pie.set_title('EEG各节律平均相对功率占比', fontsize=14)
ax_pie.axis('equal')  # 保证正圆形
plt.tight_layout()
pie_save_path = os.path.join('notebooks', '03_band_power_pie.png')
plt.savefig(pie_save_path, dpi=300, bbox_inches='tight')
plt.close(fig_pie)
print(f"\n✅ 饼图已保存：{pie_save_path}")

# 2. 绘制柱状图
fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
ax_bar.bar(bands_list, power_values, color=plot_colors)
ax_bar.set_title('EEG各节律平均相对功率', fontsize=14)
ax_bar.set_ylabel('相对功率占比 (%)', fontsize=12)
ax_bar.set_xlabel('脑电节律', fontsize=12)
ax_bar.grid(axis='y', alpha=0.3)
plt.tight_layout()
bar_save_path = os.path.join('notebooks', '03_band_power_bar.png')
plt.savefig(bar_save_path, dpi=300, bbox_inches='tight')
plt.close(fig_bar)
print(f"✅ 柱状图已保存：{bar_save_path}")

# ======================
# 6. 特征整理与保存（AI训练的核心输入）
# ======================
n_samples = len(epochs)
n_channels = len(epochs.ch_names)
n_bands = len(frequency_bands)

# 构建特征矩阵：(样本数, 通道数×节律数)
feature_matrix = np.zeros((n_samples, n_channels * n_bands))
feature_names = []

# 填充特征矩阵
for band_idx, band_name in enumerate(frequency_bands.keys()):
    for chan_idx, chan_name in enumerate(epochs.ch_names):
        feature_name = f"{chan_name}_{band_name}"
        feature_names.append(feature_name)
        feature_matrix[:, band_idx * n_channels + chan_idx] = relative_powers[band_name][:, chan_idx]

# 转成表格，方便查看
feature_df = pd.DataFrame(feature_matrix, columns=feature_names)
feature_df['sample_id'] = range(n_samples)  # 增加样本编号

# 保存特征文件
csv_save_path = os.path.join('features', 'eeg_band_power_features.csv')
feature_df.to_csv(csv_save_path, index=False)

npy_matrix_path = os.path.join('features', 'eeg_feature_matrix.npy')
np.save(npy_matrix_path, feature_matrix)

npy_names_path = os.path.join('features', 'eeg_feature_names.npy')
np.save(npy_names_path, feature_names)

# ======================
# 最终验证与输出
# ======================
print("\n📁 特征保存完成：")
print(f"- 特征表格（可直接打开查看）：{csv_save_path}")
print(f"- 特征矩阵（AI模型直接读取）：{npy_matrix_path}")
print(f"最终特征维度：{feature_matrix.shape} → {n_samples}个样本，每个样本{n_channels*n_bands}个特征")

# 验证文件是否成功生成
print("\n📂 生成的文件清单：")
print("【notebooks文件夹 可视化结果】：")
for file in os.listdir('notebooks'):
    if file.startswith('03_'):
        print(f"  - {file}")
print("【features文件夹 特征文件】：")
for file in os.listdir('features'):
    print(f"  - {file}")

print("\n🎉 EEG频域特征提取全流程100%完成！")
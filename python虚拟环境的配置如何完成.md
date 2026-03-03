# EEG-EdgeAI-Pipeline 环境搭建与Git/GitHub全流程操作手册

**适用环境**：Windows 系统、Anaconda Prompt、Python 3.9、神经科学EEG项目开发
**文档用途**：完整覆盖从「零环境搭建」到「GitHub云端同步」的全流程操作，包含所有踩坑解决方案，可直接复现、长期复用。

---

## 一、Anaconda 虚拟环境搭建（项目基础）

### 核心目的

为项目创建**独立、可复现**的Python环境，避免和系统其他项目的库版本冲突，确保项目在任何设备上都能还原相同的运行环境。

### 完整操作步骤

1. **创建虚拟环境**

&nbsp;   ```bash
    # 创建名为 neuro 的环境，指定Python 3.9（MNE等EEG处理库的稳定适配版本）
    conda create -n neuro python=3.9
    ```

   * 交互提示：出现 `Proceed (\[y]/n)?` 时，输入 `y` 按回车确认安装。
   * 成功标志：终端提示 `# To activate this environment, use` 等环境激活指引。

2. **激活虚拟环境**

&nbsp;   ```bash
    conda activate neuro
    ```

   * 成功标志：终端提示符最前方出现 `(neuro)` 标识，代表已进入该环境。

3. **安装项目核心依赖库**

&nbsp;   ```bash
    # 安装EEG神经科学处理库MNE，以及科学计算、可视化、交互式开发基础库
    conda install mne numpy scipy matplotlib jupyter
    ```

   * 交互提示：出现 `Proceed (\[y]/n)?` 时，输入 `y` 按回车，等待所有库安装完成。

4. **导出环境配置文件（核心！用于环境复现）**

&nbsp;   ```bash
    # 导出当前环境的所有库及对应版本，生成 environment.yml 配置文件
    conda env export > environment.yml
    ```

   * 核心用途：该文件上传到GitHub后，换设备/协作时，执行 `conda env create -f environment.yml` 即可一键还原完全相同的环境。

---

## 二、Git 本地仓库初始化与基础配置

### 核心目的

把本地项目文件夹转为Git仓库，记录代码的每一次变更，支持版本回溯、多人协作，是项目开发的标准规范。

### 完整操作步骤

1. **切换到项目根目录**

&nbsp;   ```bash
    # 切换到D盘（根据你的项目实际存放路径调整）
    D:
    # 进入项目文件夹
    cd GitHub\\EEG-EdgeAI-Pipeline
    ```

   * 成功标志：终端提示符变为 `(neuro) D:\\GitHub\\EEG-EdgeAI-Pipeline>`。

2. **初始化Git仓库**

&nbsp;   ```bash
    git init
    ```

   * 成功标志：终端提示 `Initialized empty Git repository in D:/GitHub/EEG-EdgeAI-Pipeline/.git/`。

3. **配置Git全局用户信息（必须配置，否则无法提交代码）**

&nbsp;   ```bash
    # 配置用户名，和你的GitHub账号名称完全一致
    git config --global user.name "HollyCNNOne"
    # 配置邮箱，和你的GitHub注册邮箱完全一致
    git config --global user.email "2024828891@qq.com"
    ```

   * 验证命令：`git config --global --list`，可查看已配置的用户信息是否正确。

4. **添加文件到Git暂存区**

&nbsp;   ```bash
    # 添加单个指定文件（推荐，精准控制提交内容）
    git add environment.yml
    # 或添加当前目录下所有变更文件
    git add .
    ```

5. **提交变更到本地Git仓库**

&nbsp;   ```bash
    # -m 后必须填写提交说明，清晰记录本次提交的内容，方便后续回溯
    git commit -m "feat: init neuro env with MNE/NumPy/SciPy base libraries"
    ```

   * 成功标志：终端提示 `1 file changed, xxx insertions(+)`，代表提交成功。

---

## 三、GitHub 远程仓库创建与关联

### 核心目的

把本地仓库和GitHub云端仓库绑定，实现代码云端备份、开源分享、多人协作。

### 完整操作步骤

1. **GitHub网页端创建远程仓库**

   1. 登录GitHub账号，点击右上角 `+` → `New repository`
   2. 仓库配置：

      * Repository name：`EEG-EdgeAI-Pipeline`（和本地项目名一致）
      * 可见性：选择 `Public`（公开）或 `Private`（私有）
      * 勾选 `Add a README file`（自动生成远程README文件，作为项目说明）

   3. 点击 `Create repository` 完成创建。

2. **本地仓库关联远程仓库**

&nbsp;   ```bash
    # 方式1：HTTPS格式（新手入门用，无需额外配置）
    git remote add origin https://github.com/HollyCNNOne/EEG-EdgeAI-Pipeline.git

    # 方式2：SSH格式（推荐长期使用，配置后无需重复认证，无SSL连接问题）
    git remote add origin git@github.com:HollyCNNOne/EEG-EdgeAI-Pipeline.git
    ```

   * 验证命令：`git remote -v`，可查看已关联的远程仓库地址。

3. **首次代码推送（常见问题提前说明）**

&nbsp;   ```bash
    # 推送到远程main分支，并设置上游分支（后续可直接用git push/pull）
    git push -u origin main
    ```

   * 高频报错：`! \[rejected] main -> main (non-fast-forward)`
   * 报错原因：远程仓库有README.md文件，本地仓库没有，两者提交历史不一致，Git为了防止覆盖远程内容，拒绝直接推送。

---

## 四、核心问题排查与解决方案（全踩坑记录）

### 问题1：non-fast-forward 推送被拒绝

#### 报错信息

```
! \[rejected] main -> main (non-fast-forward)
error: failed to push some refs to 'xxx'
hint: Updates were rejected because the tip of your current branch is behind its remote counterpart.
```

#### 核心原因

本地分支的提交历史落后于远程分支，需要先把远程的变更拉到本地合并后，再推送。

#### 解决方案

```bash
# 拉取远程代码，允许合并不相关的提交历史（本地和远程分别初始化的场景必须加）
git pull origin main --allow-unrelated-histories
```

* 避坑技巧：绕开Vim编辑器弹窗，直接指定合并提交信息

```bash
  git pull origin main --allow-unrelated-histories -m "merge: combine local env file with remote README"
  ```

* 合并完成后，重新执行推送命令即可：`git push -u origin main`

---

### 问题2：SSL/TLS 连接握手失败

#### 报错信息

```
fatal: unable to access 'https://github.com/xxx.git/': schannel: failed to receive handshake, SSL/TLS connection failed
```

#### 核心原因

国内网络环境下，Git与GitHub的HTTPS加密连接不稳定、DNS污染或证书验证异常。

#### 解决方案（从快到稳）

1. 临时关闭SSL证书验证（最快生效）

&nbsp;   ```bash
    git config --global http.sslVerify false
    ```

2. 切换网络：电脑连接手机热点，重新执行Git命令，排除宽带线路限制。
3. 终极方案：切换为SSH格式的远程仓库地址，彻底绕开HTTPS的SSL问题（配置方法见第五部分）。

---

### 问题3：未完成的合并导致无法拉取/推送

#### 报错信息

```
error: You have not concluded your merge (MERGE\_HEAD exists).
fatal: Exiting because of unfinished merge.
```

#### 核心原因

之前的合并操作中途中断，Git仍处于合并状态，不允许执行新的拉取/推送操作。

#### 解决方案

1. 完成未结束的合并（推荐，保留已解决的冲突）

&nbsp;   ```bash
    git commit -m "merge: finish unresolved merge process"
    ```

2. 放弃本次合并（重置状态，重新操作）

&nbsp;   ```bash
    git merge --abort
    ```

---

### 问题4：Vim编辑器卡住，无法退出/保存

#### 现象

执行合并命令后，弹出黑色的Vim编辑窗口，按任何按键都无法退出，或输入w后光标仅移动。

#### 核心原因

Vim有「普通模式」和「插入模式」，默认处于普通模式，直接输入w是光标移动命令，而非保存命令。

#### 正确的保存退出操作

1. 先按一下键盘上的 `Esc` 键，确保回到普通模式（底部无 `-- INSERT --` 标识）；
2. 输入英文冒号 `:`，此时窗口底部会出现冒号提示符；
3. 输入 `wq`，然后按 `Enter` 回车，即可完成保存并退出。

* 强制退出（不保存）：按 `Esc` → 输入 `:q!` → 按 `Enter`。

---

## 五、SSH 密钥配置（永久解决GitHub连接问题）

### 核心目的

用SSH密钥对代替账号密码认证，安全、稳定，无需重复输入认证信息，彻底解决HTTPS连接的各类报错。

### 完整操作步骤

1. **生成SSH密钥对**

&nbsp;   ```bash
    # 生成ed25519类型的密钥对，用GitHub注册邮箱作为标识
    ssh-keygen -t ed25519 -C "2024828891@qq.com"
    ```

   * 所有交互提示直接按回车即可：无需修改保存路径、无需设置密钥密码。
   * 成功标志：终端显示密钥的SHA256指纹和随机art图像，代表密钥生成完成。

2. **查看并复制完整公钥**
   Windows Anaconda Prompt 专用命令：

&nbsp;   ```bash
    type %userprofile%\\.ssh\\id\_ed25519.pub
    ```

   * 关键要求：完整复制输出的**整行内容**（从 `ssh-ed25519` 开头，到你的注册邮箱结尾，一个字符都不能多、不能少）。

3. **添加公钥到GitHub账号**

   1. 登录GitHub网页，进入 `Settings` → 左侧菜单栏 `SSH and GPG keys`；
   2. 点击绿色 `New SSH key` 按钮；
   3. 填写配置：

      * Title：自定义名称，比如 `Windows-PC`（标识设备）
      * Key type：保持默认的 `Authentication Key`
      * Key：粘贴刚才复制的完整公钥内容

   4. 点击 `Add SSH key` 完成添加。

4. **测试SSH连接是否成功**

&nbsp;   ```bash
    ssh -T git@github.com
    ```

   * 交互提示：出现 `Are you sure you want to continue connecting (yes/no)?` 时，输入 `yes` 按回车。
   * ✅ 成功标志：终端显示 `Hi HollyCNNOne! You've successfully authenticated`，代表SSH配置完全生效。

---

## 六、项目开发标准Git工作流（后续开发必遵循）

养成固定的开发习惯，避免冲突、版本混乱，每一次提交都可追溯：

1. **开发前同步远程最新代码**

&nbsp;   ```bash
    git pull origin main
    ```

2. **完成代码开发/修改**
3. **查看本次变更内容**

&nbsp;   ```bash
    git status
    ```

4. **添加变更文件到暂存区**

&nbsp;   ```bash
    git add 你的文件名
    # 或添加所有变更文件
    git add .
    ```

5. **提交变更到本地仓库**

&nbsp;   ```bash
    git commit -m "清晰的提交说明，比如 feat: add EEG signal filtering script"
    ```

6. **推送到GitHub远程仓库**

&nbsp;   ```bash
    git push origin main
    ```

---

## 附录1：常用命令速查表

|操作场景|核心命令|
|-|-|
|激活项目虚拟环境|`conda activate neuro`|
|退出虚拟环境|`conda deactivate`|
|初始化Git仓库|`git init`|
|查看仓库状态|`git status`|
|查看Git配置信息|`git config --global --list`|
|关联远程仓库|`git remote add origin 仓库地址`|
|查看已关联的远程仓库|`git remote -v`|
|拉取远程最新代码|`git pull origin main`|
|推送代码到远程|`git push -u origin main`|
|清空终端屏幕（Windows）|`cls`|
|清空终端屏幕（Linux/macOS）|`clear`|

---

## 附录2：Vim编辑器基础操作

|操作|按键/命令|
|-|-|
|从插入模式切回普通模式|`Esc` 键|
|进入插入模式（可编辑文本）|按 `i` 键|
|保存文件|普通模式下输入 `:w` 按回车|
|退出编辑器|普通模式下输入 `:q` 按回车|
|保存并退出|普通模式下输入 `:wq` 按回车|
|强制退出不保存|普通模式下输入 `:q!` 按回车|

---

### 文档保存与上传到GitHub的方法

1. 把以上内容完整复制，用记事本/VS Code打开，保存为 `项目操作全流程手册.md`，放在你的项目根目录下；
2. 执行以下命令，把手册上传到GitHub仓库：

&nbsp;   ```bash
    git add "项目操作全流程手册.md"
    git commit -m "docs: add full operation manual for env and git"
    git push origin main
    ```

3. 刷新GitHub仓库页面，即可在线查看、随时复用这份手册。

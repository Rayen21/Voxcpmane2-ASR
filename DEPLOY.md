# VoxCPM2 本地部署记录

## 基本信息
- **项目**: VoxCPMANE2 (VoxCPM2 TTS Server)
- **GitHub**: https://github.com/0seba/VoxCPMANE
- **本地设备**: M1 Max

---

## 工作路径（核心）

本项目涉及两个目录，**必须严格区分**：

| 目录 | 路径 | 用途 |
|------|------|------|
| **安装目录** | `/Users/hanqingren/miniforge3/envs/voxcpm2` | **真实运行的项目目录**，服务器从这里启动，前端从这里加载 |
| **仓库目录** | `/Users/hanqingren/voxcpm` | 从 GitHub 拉取的源码目录，仅用于开发修改 |

### 关键规则
1. **启动服务器**：`voxcpm2-server` 命令从 conda 环境激活后执行，实际运行的是安装目录中的代码
2. **修改代码**：前端 UI 修改、代码编辑都在 `/Users/hanqingren/voxcpm` 中进行
3. **修改后必须同步到安装目录**：在仓库目录修改完前端后，**必须手动复制**到安装目录才能生效
---

## M1 设备兼容性问题（核心）

M1 设备使用标准版本（0.1.2）启动时会报错：
```
RuntimeError: `MLModelConfiguration`'s `.functionName` property must be `nil`
unless the model type is ML Program.
```

### 解决方案
**必须安装 0.1.3b1 beta 版本**，并使用 `--split-base-lm` 参数：

```bash
uv tool install --python '>=3.10,<3.13' --prerelease allow -U 'voxcpmane2==0.1.3b1' voxcpmane2-server --split-base-lm
```

---

## 快速启动

```bash
cd /Users/hanqingren/voxcpm
eval "$(conda shell.bash hook)" && conda activate voxcpm2
voxcpmane2-server --split-base-lm --port 8000
```

### 使用本地模型目录（跳过下载）
```bash
SNAPSHOT="/Users/hanqingren/.cache/huggingface/hub/models--seba--VoxCPM2ANE-Preview/snapshots/def350ecae1aa3e4028970a5eae8faa7b3800d40"
voxcpmane2-server --model-dir "$SNAPSHOT" --split-base-lm
```

---

## 环境配置

- **Conda 环境**: voxcpm2 (Python 3.11)
- **安装方式**: `pip install -e .` (editable mode)
- **环境路径**: /Users/hanqingren/miniforge3/envs/voxcpm2

### 依赖包
coremltools==9.0, numpy>=2, ml-dtypes>=0.5.0, soundfile, soxr>=1.0.0, tokenizers, fastapi, uvicorn, aiofiles, huggingface_hub, sounddevice, ftfy>=6.3.1, inflect, wetext, regex

---

## 模型缓存
- **HF 缓存 (主模型)**: ~/.cache/huggingface/hub/models--seba--VoxCPM2ANE-Preview
- **HF 缓存 (split BaseLM)**: ~/.cache/huggingface/hub/models--seba--VoxCPMANE2-Debug-Models
- **自定义声音缓存**: ~/.cache/ane_tts

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | Web 前端页面 |
| GET | /health | 服务器健康检查 |
| GET | /voices | 获取可用声音列表 |
| POST | /v1/audio/speech | 生成完整音频 |
| POST | /v1/audio/speech/stream | 流式传输 PCM16 音频 |
| POST | /v1/audio/speech/cancel | 取消当前生成 |
| POST | /v1/voices | 创建自定义声音 |
| DELETE | /v1/voices/{name} | 删除自定义声音 |

---

## LM 模式选项

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| single-length (默认) | 使用相同长度进行预填充和解码 | 默认推荐 |
| preload | 预加载长度 1 和预填充大小 | 追求最佳 RTF |
| always-loaded | 始终保留长度 1 和预填充大小 | 最快响应 |
| hot-swap | 空闲时预加载，解码时切换 | 内存受限时 |

---

## 声音管理模式

| 模式 | 说明 | 延迟 | 质量 |
|------|------|------|------|
| reference | 仅参考音频 | 最低 | 好 |
| reference_plus_prompt | 参考 + 提示音频 | 中等 | 更好 |
| high_similarity | 高相似度（使用转录） | 最高 | 最好 |

---

## 注意事项

1. CoreML 首次加载模型可能需要几分钟
2. **M1 设备必须使用 `--split-base-lm` 参数**
3. 建议启动时使用 `--lm-mode preload` 获得最佳性能
4. 自定义声音存储在 ~/.cache/ane_tts
5. **修改前端后必须同步到安装目录才能生效**
6. **服务器端口统一为 8000**，前端 API_BASE_URL 必须配置为 `http://localhost:8000`

---

## 版本说明

- **源码版本** (`pyproject.toml`): 0.1.2（仅作为项目版本记录）
- **本地安装版本**: 0.1.3b1 beta（M1 设备必须使用此版本）

所有测试、前端修改和功能验证均针对 0.1.3b1 安装版进行。

---

## 前端修改记录（2026-09-11）

### UI 修复
- **骰子图标** — `.dice-icon` class 保持 `font-size: 20px`；开启自动随机时蓝色 `#0ea5e9`，关闭时灰色 `#8E8E93`（虚线骰子）
- **骰子按钮背景色** — 深色模式下设为 `rgba(58, 58, 60, 0.8)`，与随机种子输入框一致
- **右侧按钮文字颜色** — ID 选择器强制设置 `#E5E5EA` / `#3A3A3C`
- **上传区域深色模式** — 设为 `rgba(58, 58, 60, 0.8)`，与随机种子输入区统一；文件名文字颜色 `#A1A1AA`

### 功能修复
- **流式播放实时解码** — `streamAndPlay()` 改为增量解码：每收到一个 chunk 就构建 WAV blob、解码成 AudioBuffer，排队到 AudioContext 中按时间顺序播放。不再等全部数据收完才一次性播放
- **audioContext 创建时机** — 在收到响应、拿到 sampleRate 之后才创建 AudioContext（之前在全局变量为 null 时调用 decodeAudioData 报错）
- **src 变量作用域修复** — `lastSrc` 在 while 循环外声明，避免循环后引用未定义变量
- **骰子图标 class 保留** — toggleSeedMode() 中切换 icon class 时保留 `.dice-icon` 类名，防止字体大小丢失

### 功能调整
- **移除"成品创建"按钮** — 核实两个端点 `/v1/audio/speech`（非流式）和 `/v1/audio/speech/stream`（流式）生成的音频内容完全一样，统一使用"实时播放"一个入口
- **新增"下载音频"按钮** — 生成完成后自动启用，点击即可下载 `.wav` 文件

### 进度条修复
- 恢复原始 `updateProgress()` 函数：根据接收字节数实时更新进度条宽度和百分比数字
- 移除所有动画效果（呼吸/流光/脉冲），使用蓝色渐变背景 + 模拟百分比跳动

### 同步规则
所有前端修改在 `/Users/hanqingren/voxcpm/src/voxcpmane/frontend/index.html` 中进行，必须手动复制到安装目录：
```bash
cp /Users/hanqingren/voxcpm/src/voxcpmane/frontend/index.html /Users/hanqingren/miniforge3/envs/voxcpm2/lib/python3.11/site-packages/voxcpmane/frontend/index.html
```

---

## 当前状态

服务器运行中：
- 地址: http://127.0.0.1:8000
- 健康状态: 正常

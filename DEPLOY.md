# VoxCPM2 本地部署记录

## 基本信息
- **项目**: VoxCPMANE2 (VoxCPM2 TTS Server)
- **GitHub**: https://github.com/0seba/VoxCPMANE
- **本地路径**: /Users/hanqingren/voxcpm
- **本地设备**: M1 Max
- **部署日期**: 2026-09-06

## 环境配置

### Conda 环境
- **环境名称**: voxcpm2
- **Python 版本**: 3.11
- **安装方式**: `pip install -e .` (editable mode)
- **环境路径**: /Users/hanqingren/miniforge3/envs/voxcpm2

### 依赖包
- coremltools==9.0
- numpy>=2
- ml-dtypes>=0.5.0
- soundfile, soxr>=1.0.0
- tokenizers, fastapi, uvicorn
- aiofiles, huggingface_hub, sounddevice
- ftfy>=6.3.1, inflect, wetext, regex

### 项目版本
- **voxcpmane2**: 0.1.3b1 (beta)
- 使用原因: 0.1.3b1 支持 `--split-base-lm` 参数，解决 M1 设备 BaseLM 加载问题

## 模型缓存
- **HF 缓存 (主模型)**: ~/.cache/huggingface/hub/models--seba--VoxCPM2ANE-Preview
- **HF 缓存 (split BaseLM)**: ~/.cache/huggingface/hub/models--seba--VoxCPMANE2-Debug-Models
- **自定义声音缓存**: ~/.cache/ane_tts

## M1 设备配置（关键）

M1 设备需要安装 beta 版本并使用 `--split-base-lm` 参数：

```bash
# 安装 beta 版本
pip install --upgrade --pre 'voxcpmane2==0.1.3b1'

# 启动服务器（使用 split-base-lm）
voxcpmane2-server --split-base-lm
```

### 为什么需要 split-base-lm？
部分 M1 Mac 在加载完整 BaseLM CoreML 包时会失败：
```
ANE model load has failed for on-device compiled macho.
RuntimeError: MLModelConfiguration's .functionName property must be nil
```

`--split-base-lm` 会将 BaseLM 分成两个包加载，避免此问题。

## 启动方式

### 基本启动（推荐 M1）
```bash
cd /Users/hanqingren/voxcpm
eval "$(conda shell.bash hook)" && conda activate voxcpm2
voxcpmane2-server --split-base-lm
```

### 使用本地模型目录（跳过下载）
```bash
SNAPSHOT="/Users/hanqingren/.cache/huggingface/hub/models--seba--VoxCPM2ANE-Preview/snapshots/def350ecae1aa3e4028970a5eae8faa7b3800d40"
voxcpmane2-server --model-dir "$SNAPSHOT" --split-base-lm
```

### 自定义端口和参数
```bash
voxcpmane2-server --port 8000 --host 0.0.0.0
voxcpmane2-server --lm-mode preload --lm-prefill-chunk-size 32
```

## LM 模式选项

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| single-length (默认) | 使用相同长度进行预填充和解码 | 默认推荐 |
| preload | 预加载长度 1 和预填充大小 | 追求最佳 RTF |
| always-loaded | 始终保留长度 1 和预填充大小 | 最快响应 |
| hot-swap | 空闲时预加载，解码时切换 | 内存受限时 |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | Web 前端页面 |
| GET | /health | 服务器健康检查 |
| GET | /voices | 获取可用声音列表 |
| POST | /v1/audio/speech | 生成完整音频 |
| POST | /v1/audio/speech/stream | 流式传输 PCM16 音频 |
| POST | /v1/audio/speech/playback | 服务器端播放音频 |
| POST | /v1/audio/speech/cancel | 取消当前生成 |
| POST | /v1/voices | 创建自定义声音 |
| DELETE | /v1/voices/{name} | 删除自定义声音 |

## 声音管理模式

| 模式 | 说明 | 延迟 | 质量 |
|------|------|------|------|
| reference | 仅参考音频 | 最低 | 好 |
| reference_plus_prompt | 参考 + 提示音频 | 中等 | 更好 |
| high_similarity | 高相似度（使用转录） | 最高 | 最好 |

## 前端功能

新前端（已替换原前端）覆盖以下功能：
1. **语音生成** - 文本输入 + 声音选择 + 参数配置
2. **流式播放** - 实时流式生成并播放
3. **完整音频生成** - 生成完整 WAV 音频并下载
4. **服务器播放** - 在服务器端直接播放
5. **声音管理** - 查看/创建/删除自定义声音
6. **流式下载** - 下载原始 PCM16 音频文件
7. **服务器状态** - 实时显示服务器健康状态

## 操作记录

- [x] 克隆 GitHub 仓库到本地
- [x] 确认 conda 环境 voxcpm2 已创建
- [x] 安装项目依赖 (voxcpmane2 0.1.3b1)
- [x] 确认模型已下载
- [x] 重写前端界面（现代化设计）
- [x] 前端复制到安装包目录
- [x] 服务器启动测试（--split-base-lm 模式）
- [x] 健康检查通过

## 当前状态

服务器运行中：
- 地址: http://127.0.0.1:8000
- 健康状态: 正常
- 模型: voxcpm2
- LM 缓存长度: 2048
- 可用声音: 系统预设 + 自定义声音

## 注意事项

1. CoreML 首次加载模型可能需要几分钟
2. M1 设备必须使用 `--split-base-lm` 参数
3. 建议启动时使用 `--lm-mode preload` 获得最佳性能
4. 自定义声音存储在 ~/.cache/ane_tts

## 版本说明

### 源码版本 (pyproject.toml)
- 当前 `pyproject.toml` 中的版本为 **0.1.2**
- 此版本为正式稳定版，仅作为项目版本记录

### 本地安装版本
- 本地 conda 环境 `voxcpm2` 中安装的版本为 **0.1.3b1** (beta)
- 安装方式: `pip install --upgrade --pre 'voxcpmane2==0.1.3b1'`
- 使用原因: 0.1.3b1 支持 `--split-base-lm` 参数，解决 M1 设备 BaseLM 加载问题

### 重要说明
- **pyproject.toml 中的 0.1.2 版本不适用于 M1 设备**，M1 设备必须使用 0.1.3b1 beta 版本
- 本地项目源码文件夹 (`/Users/hanqingren/voxcpm`) 中的版本记录 (0.1.2) 保持原样，无需修改
- **所有测试、前端修改和功能验证均针对 0.1.3b1 安装版进行**
- 修改代码时以本地安装的 0.1.3b1 为准，pyproject.toml 版本号仅在发布时更新

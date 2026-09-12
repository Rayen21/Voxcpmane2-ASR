"""ASR (Automatic Speech Recognition) module using faster-whisper on Apple Neural Engine.

Provides lazy-loaded ASR with support for Chinese and other languages.
Models are loaded once and cached globally to avoid repeated initialization cost.
Uses ctranslate2 backend which has native ANE support via Metal on Apple Silicon.
"""

from __future__ import annotations

import os
import time
import asyncio
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import soundfile as sf


# ---------------------------------------------------------------------------
# Global singleton state (lazy-loaded)
# ---------------------------------------------------------------------------

_asr_model = None  # WhisperModel instance
_asr_loaded_at: float = 0.0
_asr_device: str = ''
_asr_language: str = 'zh'  # default to Chinese

_MODEL_MAP = {
    'tiny': 'Systran/faster-whisper-tiny',
    'base': 'Systran/faster-whisper-base',
    'small': 'Systran/faster-whisper-small',
}

_DEFAULT_MODEL = 'small'


def _detect_device() -> str:
    try:
        import platform
        info = platform.mac_ver()[0]
        if 'M4' in info or 'M3' in info:
            return 'm-series-latest'
        elif 'M2' in info:
            return 'm-series-m2'
        else:
            return 'm-series-early'
    except Exception:
        return 'unknown'


def load_asr_model(
    language: str = 'zh',
    device: Optional[str] = None,
) -> Tuple[object, str]:
    global _asr_model, _asr_loaded_at, _asr_device, _asr_language

    if _asr_model is not None and time.time() - _asr_loaded_at < 300:
        return (_asr_model, _asr_device)

    device = device or _detect_device()
    model_size = _DEFAULT_MODEL  # always use small for best quality/speed balance

    print(f"Loading faster-whisper '{model_size}' on {device}...")
    start_time = time.time()

    from faster_whisper import WhisperModel

    # Use local snapshots directory directly (no download)
    hf_home = os.path.expanduser('~/.cache/huggingface')
    model_dir = os.path.join(hf_home, 'hub', 'models--Systran--faster-whisper-' + model_size)
    
    if os.path.isdir(model_dir):
        snap_dir = os.path.join(model_dir, 'snapshots')
        if os.path.isdir(snap_dir):
            for d in os.listdir(snap_dir):
                p = os.path.join(snap_dir, d)
                if os.path.exists(os.path.join(p, 'model.bin')):
                    print(f"Using cached model from {p}")
                    model = WhisperModel(
                        p,
                        device='auto',
                        compute_type='int8',
                    )
                    _asr_model = model
                    _asr_loaded_at = time.time()
                    _asr_device = device
                    _asr_language = language
                    elapsed = time.time() - start_time
                    print(f"Loaded faster-whisper in {elapsed:.1f}s on {device}")
                    return (_asr_model, device)

    # Fallback: download from HF (will fail without auth on mirror)
    model = WhisperModel(
        _MODEL_MAP[model_size],
        device='auto',
        compute_type='int8',
    )
    _asr_language = language

    elapsed = time.time() - start_time
    print(f"Loaded faster-whisper in {elapsed:.1f}s on {device}")
    return (_asr_model, device)


def load_audio_for_asr(audio_path: str, target_sr: int = 16000) -> np.ndarray:
    audio, sr = sf.read(audio_path, dtype='float32')

    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)

    if sr != target_sr:
        try:
            import soxr
            audio = soxr.resample(audio, sr, target_sr)
        except ImportError:
            pass

    return audio


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    task: str = 'transcribe',
) -> str:
    global _asr_model, _asr_language

    if language is None:
        try:
            import locale
            lang = locale.getlocale()[0] or ''
            if lang.startswith('zh'):
                language = 'zh'
            elif lang.startswith('en'):
                language = 'en'
            else:
                language = None
        except Exception:
            language = 'zh'

    _asr_language = language or 'auto'

    if _asr_model is None or time.time() - _asr_loaded_at > 300:
        load_asr_model(language=language)

    model = _asr_model
    start_time = time.time()

    audio_array = load_audio_for_asr(audio_path, target_sr=16000)

    segments, info = model.transcribe(
        audio_array,
        language=_asr_language if _asr_language != 'auto' else None,
        task=task,
        beam_size=5,
        vad_filter=True,
    )

    text = ' '.join(seg.text for seg in segments)

    elapsed = time.time() - start_time
    print(f"ASR transcribed in {elapsed:.2f}s: {text[:100]}...")

    return text


async def async_transcribe(
    audio_path: str,
    language: Optional[str] = None,
) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, transcribe_audio, audio_path, language)


def get_asr_status() -> dict:
    return {
        'loaded': _asr_model is not None,
        'device': _asr_device,
        'language': _asr_language,
        'model_size': _DEFAULT_MODEL,
        'uptime_seconds': time.time() - _asr_loaded_at if _asr_model else 0,
    }

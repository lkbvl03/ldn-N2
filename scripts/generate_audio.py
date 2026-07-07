"""
Nhạc nền cinematic tâm lý học — Kênh LDN
Video: "Tại Sao Bạn Nhớ Lời Chỉ Trích Lâu Hơn Lời Khen"
Thời lượng: 1080s (18 phút) — bao phủ video ~16 phút + buffer
Output: public/background-music.wav
Chạy: python -X utf8 scripts/generate_audio.py

Cấu trúc 7 đoạn cảm xúc theo kịch bản:
  A  0 – 90s    : Đêm khuya · phòng ngủ tối (tối, chậm, bất an)
  B  90 – 145s  : Hook câu hỏi (căng thẳng nhẹ, tò mò)
  C  145 – 480s : Amygdala + Cortisol (khoa học tối, xung nhịp não)
  D  480 – 665s : Zeigarnik + Rumination (vòng lặp ám ảnh)
  E  665 – 900s : Schema + Gottman (nặng nề, tích lũy)
  F  900 – 1120s: Neuroplasticity (chuyển dần sang hy vọng)
  G  1120– 1080s: Bài học + Kết (ấm, nhẹ, tự do)
"""
import sys, os, wave
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

SR     = 44100
PUBLIC = os.path.join(os.path.dirname(__file__), '..', 'public')
os.makedirs(PUBLIC, exist_ok=True)

TOTAL_SEC = 1080   # 18 phút


# ── Tiện ích ──────────────────────────────────────────────────────────────────

def save_wav(path, data):
    data = np.clip(data, -1.0, 1.0)
    pcm  = (data * 32767).astype(np.int16)
    if pcm.ndim == 1:
        pcm = np.stack([pcm, pcm], axis=1)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"  Saved: {os.path.basename(path)}  ({size_mb:.1f} MB, {len(data)/SR:.0f}s)")

def sine(f, n, phi=0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + phi)

def noise_lp(n, cutoff_hz):
    """White noise qua lowpass 1-pole."""
    nz  = np.random.uniform(-1, 1, n)
    a   = 1 / (2 * np.pi * cutoff_hz / SR + 1)
    out = np.zeros(n)
    out[0] = nz[0]
    for i in range(1, n):
        out[i] = a * out[i - 1] + (1 - a) * nz[i]
    return out

def fade(sig, in_sec=0, out_sec=0):
    s = sig.copy()
    if in_sec:
        ni = min(int(in_sec * SR), len(s))
        s[:ni] *= np.linspace(0, 1, ni)
    if out_sec:
        no = min(int(out_sec * SR), len(s))
        s[-no:] *= np.linspace(1, 0, no)
    return s

def xfade(a, b, overlap_sec):
    """Cross-fade cuối a với đầu b."""
    ov = int(overlap_sec * SR)
    ramp_in  = np.linspace(0, 1, ov)
    ramp_out = np.linspace(1, 0, ov)
    out      = a.copy()
    out[-ov:] *= ramp_out
    b2         = b.copy()
    b2[:ov]   *= ramp_in
    return np.concatenate([out[:-ov], out[-ov:] + b2[:ov], b2[ov:]])

def place(total, sig, start_sec):
    """Đặt sig vào vị trí start_sec trong mảng total."""
    s = int(start_sec * SR)
    e = min(s + len(sig), len(total))
    total[s:e] += sig[:e - s]

def stereo_width(mono, delay_ms=12):
    """Tạo stereo từ mono bằng Haas effect."""
    delay = int(delay_ms * SR / 1000)
    left  = mono.copy()
    right = np.concatenate([np.zeros(delay), mono[:-delay]])
    return np.stack([left, right], axis=1)


# ── Nhạc nền ─────────────────────────────────────────────────────────────────

def generate_bgm():
    N = int(TOTAL_SEC * SR)
    t = np.arange(N) / SR
    mix = np.zeros(N)

    print(f"Đang tạo nhạc nền {TOTAL_SEC}s ({TOTAL_SEC/60:.1f} phút)...")

    # ── LAYER 1: Bass drone xuyên suốt (Am — A2=110Hz) ──────────────────────
    # Thở rất chậm — LFO 0.07Hz (~14s/chu kỳ)
    drone = (0.22 * sine(110, N) +
             0.09 * sine(220, N) +
             0.04 * sine(330, N))
    lfo_breath = 0.70 + 0.30 * np.sin(2 * np.pi * 0.07 * t)
    drone *= lfo_breath
    # Đoạn F-G tăng nhẹ ấm hơn (chuyển sang D major = 146Hz)
    seg_F = int(900 * SR)
    ramp_FG = np.zeros(N)
    ramp_FG[seg_F:] = np.linspace(0, 1, N - seg_F)
    drone_warm = (0.18 * sine(146.8, N) +
                  0.08 * sine(293.7, N)) * ramp_FG * lfo_breath
    mix += fade(drone, in_sec=4, out_sec=8) * 0.9
    mix += drone_warm * 0.5

    # ── LAYER 2: Neural pulse — 0.8Hz đến 1.2Hz ─────────────────────────────
    # Tần số nhịp tim/não — tăng dần từ đoạn C
    pulse_freq = 0.8 + 0.4 * np.clip((t - 145) / 300, 0, 1)
    pulse_phase = 2 * np.pi * np.cumsum(pulse_freq) / SR
    pulse_env = (np.sin(pulse_phase) * 0.5 + 0.5) ** 2
    pulse = sine(55, N) * pulse_env * 0.10
    # Tắt dần từ đoạn F (900s)
    pulse_fade = np.clip(1 - (t - 900) / 220, 0, 1)
    mix += pulse * pulse_fade

    # ── LAYER 3: Đoạn A — Phòng ngủ (0–90s) ────────────────────────────────
    # Tối, im lặng, chỉ có một pad Dm mờ
    n_A = int(90 * SR)
    t_A = np.arange(n_A) / SR
    pad_A = (0.14 * np.sin(2*np.pi*146.8*t_A) +
             0.10 * np.sin(2*np.pi*174.6*t_A) +
             0.07 * np.sin(2*np.pi*220.0*t_A))
    pad_A = fade(pad_A, in_sec=6, out_sec=10) * 0.85
    place(mix, pad_A, 0)

    # ── LAYER 4: Đoạn B — Hook (90–145s) ───────────────────────────────────
    # Căng thẳng nhẹ, câu hỏi xuất hiện — tritone interval
    n_B = int(55 * SR)
    t_B = np.arange(n_B) / SR
    # Tritone: C-F# (130.8 – 185.0) gây cảm giác bất ổn
    tritone = (0.12 * np.sin(2*np.pi*130.8*t_B) +
               0.10 * np.sin(2*np.pi*185.0*t_B))
    lfo_B = 1 + 0.08 * np.sin(2*np.pi*0.5*t_B)
    tritone = fade(tritone * lfo_B, in_sec=4, out_sec=8) * 0.7
    place(mix, tritone, 90)

    # ── LAYER 5: Đoạn C — Amygdala + Cortisol (145–480s) ───────────────────
    # Xung nhịp não, tối dần, khoa học lạnh
    n_C = int(335 * SR)
    t_C = np.arange(n_C) / SR
    # Am minor: A-C-E (220-261.6-329.6)
    sci_pad = (0.11 * np.sin(2*np.pi*220.0*t_C) +
               0.08 * np.sin(2*np.pi*261.6*t_C) +
               0.06 * np.sin(2*np.pi*329.6*t_C))
    # Tension climber tại mốc cortisol (t=80s của đoạn C → 225s tổng)
    chirp_f = 160 + 80 * (t_C / 335) ** 1.5
    chirp_p = 2 * np.pi * np.cumsum(chirp_f) / SR
    chirp   = np.sin(chirp_p) * 0.04
    # Low filtered noise — sub-cortex texture
    sub_nz = noise_lp(n_C, 120) * 0.035
    seg_C = sci_pad + chirp + sub_nz
    seg_C = fade(seg_C, in_sec=8, out_sec=10)
    place(mix, seg_C * 0.75, 145)

    # ── LAYER 6: Đoạn D — Zeigarnik Loop (480–665s) ─────────────────────────
    # Vòng lặp ám ảnh — ostinato piano-like (sine thập phân)
    n_D = int(185 * SR)
    t_D = np.arange(n_D) / SR
    # Ostinato 3 nốt lặp lại (E-D-C# mỗi 1.5s)
    loop_period = 1.5
    ostinato = np.zeros(n_D)
    for k in range(int(185 / loop_period) + 1):
        st = int(k * loop_period * SR)
        dur_note = int(0.4 * SR)
        notes = [329.6, 293.7, 277.2]   # E-D-C# (lẩn quẩn)
        for j, nf in enumerate(notes):
            ns = st + j * int(0.5 * SR)
            ne = min(ns + dur_note, n_D)
            if ns >= n_D: break
            seg_t = np.arange(ne - ns) / SR
            note  = np.sin(2*np.pi*nf*seg_t) * np.exp(-4*seg_t) * 0.18
            ostinato[ns:ne] += note
    # Dark pad bên dưới
    d_pad = (0.10 * np.sin(2*np.pi*138.6*t_D) +
             0.07 * np.sin(2*np.pi*164.8*t_D))
    d_pad *= (1 + 0.06 * np.sin(2*np.pi*0.3*t_D))
    seg_D = ostinato + d_pad
    seg_D = fade(seg_D, in_sec=6, out_sec=8)
    place(mix, seg_D * 0.80, 480)

    # ── LAYER 7: Đoạn E — Schema + Gottman (665–900s) ───────────────────────
    # Nặng nề, tích lũy — low cello-like tones
    n_E = int(235 * SR)
    t_E = np.arange(n_E) / SR
    # Cello-like: Am - Dm - Am (16s mỗi chord)
    chords = [(220, 261.6, 329.6), (146.8, 174.6, 220.0), (220, 261.6, 329.6)]
    cello = np.zeros(n_E)
    chord_dur = int(16 * SR)
    for ci, chord in enumerate(chords * 5):
        cs = ci * chord_dur
        ce = min(cs + chord_dur, n_E)
        if cs >= n_E: break
        for fi in chord:
            seg_t = np.arange(ce - cs) / SR
            vib   = 1 + 0.008 * np.sin(2*np.pi*5.5*seg_t)
            cello[cs:ce] += np.sin(2*np.pi*fi*seg_t) * vib * 0.08
    # Crescendo nhẹ ở giữa đoạn E (pattern interrupt 2 — số 4:1)
    cresc = 1 + 0.35 * np.clip((t_E - 80) / 40, 0, 1) * np.clip(1 - (t_E - 150) / 40, 0, 1)
    seg_E = cello * cresc
    seg_E = fade(seg_E, in_sec=8, out_sec=10)
    place(mix, seg_E * 0.78, 665)

    # ── LAYER 8: Đoạn F — Neuroplasticity (900–1120s) ───────────────────────
    # Chuyển từ tối sang hy vọng — D major (146.8-184.9-220-246.9)
    n_F = int(220 * SR)
    t_F = np.arange(n_F) / SR
    # Bắt đầu tối (Am) chuyển sang sáng (D) trong 90s
    ratio = np.clip(t_F / 90, 0, 1)
    hope_pad = ((1 - ratio) * (0.12 * np.sin(2*np.pi*220.0*t_F) +
                                0.08 * np.sin(2*np.pi*261.6*t_F)) +
                ratio       * (0.12 * np.sin(2*np.pi*146.8*t_F) +
                                0.08 * np.sin(2*np.pi*184.9*t_F) +
                                0.07 * np.sin(2*np.pi*220.0*t_F) +
                                0.05 * np.sin(2*np.pi*246.9*t_F)))
    lfo_F = 1 + 0.05 * np.sin(2*np.pi*0.15*t_F)
    hope_pad *= lfo_F
    # High shimmer — neural spark (bright 2093Hz crystal)
    shimmer = np.sin(2*np.pi*2093*t_F) * np.clip(ratio - 0.4, 0, 1) * 0.025
    seg_F = hope_pad + shimmer
    seg_F = fade(seg_F, in_sec=10, out_sec=8)
    place(mix, seg_F * 0.80, 900)

    # ── LAYER 9: Đoạn G — Bài học + Kết (1020–1080s end) ───────────────────
    n_G = int((TOTAL_SEC - 1020) * SR)
    t_G = np.arange(n_G) / SR
    # Ấm, G major (196-246.9-293.7-392) — nhẹ nhàng
    warm = (0.14 * np.sin(2*np.pi*196.0*t_G) +
            0.10 * np.sin(2*np.pi*246.9*t_G) +
            0.07 * np.sin(2*np.pi*293.7*t_G) +
            0.04 * np.sin(2*np.pi*392.0*t_G))
    lfo_G = 1 + 0.04 * np.sin(2*np.pi*0.2*t_G)
    warm *= lfo_G
    # Gentle high melody — serenade phrase (784Hz = G5, thỉnh thoảng)
    mel = np.zeros(n_G)
    mel_notes = [(0, 784, 1.5), (2, 698.5, 1.0), (3.5, 659.3, 2.0),
                 (6, 784, 1.5), (8, 880.0, 1.0), (9.5, 784, 2.5)]
    for rep in range(int(n_G / SR / 12) + 1):
        for (st_s, f, dur_s) in mel_notes:
            st = int((rep * 12 + st_s) * SR)
            en = min(st + int(dur_s * SR), n_G)
            if st >= n_G: break
            seg_t = np.arange(en - st) / SR
            mel[st:en] += (np.sin(2*np.pi*f*seg_t) *
                           np.exp(-1.2*seg_t) * 0.045)
    warm_seg = fade(warm + mel, in_sec=8, out_sec=15)
    place(mix, warm_seg * 0.82, 1020)

    # ── LAYER 10: Ambient texture xuyên suốt ────────────────────────────────
    sub_tex = noise_lp(N, 80) * 0.020
    mix += sub_tex

    # ── Normalize tổng hợp ──────────────────────────────────────────────────
    mix = fade(mix, in_sec=3, out_sec=10)
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.34   # -9.4 dBFS — để headroom cho giọng đọc

    # ── Stereo ──────────────────────────────────────────────────────────────
    stereo = stereo_width(mix, delay_ms=15)

    out_path = os.path.join(PUBLIC, 'background-music.wav')
    save_wav(out_path, stereo)
    print("  → Volume khuyến nghị trong video: 0.12 – 0.18")
    print(f"  → Dùng chung cho toàn bộ video ({TOTAL_SEC//60} phút {TOTAL_SEC%60}s)")


# ── Chạy ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  NHẠC NỀN — LDN — Negativity Bias Video")
    print("=" * 60)
    generate_bgm()
    print("\nHOÀN THÀNH!")

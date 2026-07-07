"""
12 SFX Cinematic — Video "Tại Sao Bạn Nhớ Lời Chỉ Trích Lâu Hơn Lời Khen"
Kênh Lạ Đời Nhất (LDN) — Tâm lý học não bộ

SFX MAP theo kịch bản:
  sfx_01_bedroom_night      → Hook mở đầu: phòng ngủ tối, bất an
  sfx_02_question_rise      → Câu hỏi gây tò mò xuất hiện
  sfx_03_amygdala_fire      → Amygdala khai hỏa (180ms)
  sfx_04_threat_detected    → Não bộ nhận diện mối đe dọa
  sfx_05_cortisol_surge     → Cortisol tràn vào hệ thống
  sfx_06_memory_engrave     → Ký ức được khắc sâu (McGaugh)
  sfx_07_zeigarnik_loop     → Vòng lặp Zeigarnik — chưa xong
  sfx_08_ratio_shock        → Con số 4-5:1 xuất hiện gây sốc
  sfx_09_schema_click       → Khuôn nhận thức schema khớp vào
  sfx_10_pattern_interrupt  → Pattern interrupt — gây chú ý
  sfx_11_neuroplasticity    → Đường thần kinh mới hình thành
  sfx_12_warm_closing       → Kết ấm: tự nói chuyện với bản thân

Output: public/sfx/sfx_*.wav + sfx-config.json
Chạy  : python -X utf8 scripts/generate_sfx2.py
"""
import sys, os, wave, json
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

SR  = 44100
DIR = os.path.join(os.path.dirname(__file__), '..', 'public', 'sfx')
os.makedirs(DIR, exist_ok=True)


# ── Tiện ích ──────────────────────────────────────────────────────────────────

def save(name, sig, note=""):
    sig  = np.clip(sig, -1.0, 1.0)
    pcm  = (sig * 32767).astype(np.int16)
    if pcm.ndim == 1:
        pcm = np.stack([pcm, pcm], axis=1)
    path = os.path.join(DIR, name)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    kb = os.path.getsize(path) // 1024
    dur = len(sig) / SR
    print(f"  {name:<38} {dur:.1f}s  {kb} KB   {note}")

def t_(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)

def sine(f, dur, phi=0):
    return np.sin(2 * np.pi * f * t_(dur) + phi)

def noise(dur):
    return np.random.uniform(-1, 1, int(SR * dur))

def norm(sig, pk=0.88):
    mx = np.max(np.abs(sig))
    return sig / (mx + 1e-9) * pk

def adsr(dur, atk=0.02, dec=0.1, sus=0.7, rel=0.2):
    n = int(SR * dur)
    a, d, r = int(SR * atk), int(SR * dec), int(SR * rel)
    s = max(0, n - a - d - r)
    e = np.zeros(n)
    if a: e[:a]             = np.linspace(0, 1, a)
    if d: e[a:a+d]          = np.linspace(1, sus, d)
    if s: e[a+d:a+d+s]      = sus
    if r: e[a+d+s:a+d+s+r]  = np.linspace(sus, 0, min(r, n - a - d - s))
    return e

def lp(sig, cutoff):
    a = 1 / (2 * np.pi * cutoff / SR + 1)
    out = np.zeros(len(sig)); out[0] = sig[0]
    for i in range(1, len(sig)):
        out[i] = a * out[i-1] + (1 - a) * sig[i]
    return out

def reverb(sig, delay_s=0.08, decay=0.4, taps=4):
    out = sig.copy().astype(float)
    d   = int(SR * delay_s)
    for i in range(1, taps + 1):
        off = d * i
        if off < len(sig):
            out[off:] += sig[:len(sig) - off] * (decay ** i)
    return out / (np.max(np.abs(out)) + 1e-9)

def stereo(mono, delay_ms=10):
    d = int(delay_ms * SR / 1000)
    L = mono.copy()
    R = np.concatenate([np.zeros(d), mono[:-d]])
    return np.stack([L, R], axis=1)


# ══════════════════════════════════════════════════════════════════════════════
# 1. sfx_01_bedroom_night — 4s
#    Khoảnh khắc quen thuộc: phòng ngủ tối, bất an trước khi ngủ
#    Cảm giác: im lặng nặng nề, có điều gì đó chưa xong
# ══════════════════════════════════════════════════════════════════════════════
def sfx_01():
    dur = 4.0
    tt  = t_(dur)
    # Sub drone Am — nặng, tối
    drone = (0.30 * sine(110, dur) +
             0.12 * sine(220, dur) +
             0.05 * sine(55,  dur))
    lfo   = 0.70 + 0.30 * np.sin(2*np.pi*0.15*tt)
    drone *= lfo
    # Distant clock tick — 1Hz (giây đang trôi)
    tick  = np.zeros(int(SR * dur))
    for i in range(4):
        st = int(i * SR)
        seg_t = np.arange(min(int(0.04*SR), len(tick)-st)) / SR
        tick[st:st+len(seg_t)] += np.sin(2*np.pi*1800*seg_t) * np.exp(-80*seg_t) * 0.18
    # Low filtered whisper noise
    whisp = lp(noise(dur), 150) * 0.04
    sig = drone + tick + whisp
    sig = reverb(sig, 0.30, 0.55, 5)
    n = len(sig)
    sig[:int(1.5*SR)] *= np.linspace(0, 1, int(1.5*SR))
    sig[-int(1.0*SR):] *= np.linspace(1, 0, int(1.0*SR))
    save('sfx_01_bedroom_night.wav', stereo(norm(sig), 20), "Phòng ngủ tối · hook mở đầu")


# ══════════════════════════════════════════════════════════════════════════════
# 2. sfx_02_question_rise — 2.5s
#    Câu hỏi lạ xuất hiện: "Tại sao một câu chỉ trích xóa mười lời khen?"
#    Cảm giác: tò mò, nghi vấn, ngứa não
# ══════════════════════════════════════════════════════════════════════════════
def sfx_02():
    dur = 2.5
    tt  = t_(dur)
    # Rising tritone — bất ổn, câu hỏi chưa có đáp án
    f_rise = 220 + 160 * (tt / dur) ** 1.2
    phase  = 2*np.pi * np.cumsum(f_rise) / SR
    riser  = np.sin(phase) * adsr(dur, 0.1, 0.3, 0.5, 0.6) * 0.35
    # High ping — "ding!" nhẹ gây chú ý
    ping   = (np.sin(2*np.pi*1760*tt) * np.exp(-6*tt) * 0.25 +
              np.sin(2*np.pi*2093*tt) * np.exp(-8*tt) * 0.15)
    sig    = riser + ping
    sig    = reverb(sig, 0.10, 0.35, 3)
    sig[-int(0.4*SR):] *= np.linspace(1, 0, int(0.4*SR))
    save('sfx_02_question_rise.wav', stereo(norm(sig), 12), "Câu hỏi tò mò · hook chính")


# ══════════════════════════════════════════════════════════════════════════════
# 3. sfx_03_amygdala_fire — 3s
#    Amygdala khai hỏa trong 180ms — mốc khoa học quan trọng nhất
#    Cảm giác: điện, chớp, tức thì — như công tắc bật
# ══════════════════════════════════════════════════════════════════════════════
def sfx_03():
    dur = 3.0
    tt  = t_(dur)
    # Electric spark — bắt đầu tại 0s
    spark_len = int(0.18 * SR)   # đúng 180ms
    spark_t   = np.arange(spark_len) / SR
    spark     = (np.sin(2*np.pi*440*spark_t * (1 + 3*spark_t)) *
                 np.exp(-15*spark_t) * 0.70)
    sig = np.zeros(int(SR * dur))
    sig[:spark_len] = spark
    # Neural alarm: 3kHz burst ngay sau spark
    alarm = np.sin(2*np.pi*3000*tt) * np.exp(-8*tt) * 0.18
    # Sub boom — vật lý của phản ứng
    boom  = np.sin(2*np.pi*55*tt) * np.exp(-3*tt) * 0.30
    sig   = sig + alarm + boom
    sig   = reverb(sig, 0.06, 0.40, 4)
    sig[-int(0.5*SR):] *= np.linspace(1, 0, int(0.5*SR))
    save('sfx_03_amygdala_fire.wav', stereo(norm(sig), 8), "Amygdala khai hỏa · 180ms")


# ══════════════════════════════════════════════════════════════════════════════
# 4. sfx_04_threat_detected — 2s
#    Não bộ nhận diện mối đe dọa (sư tử / lời chỉ trích)
#    Cảm giác: cảnh báo, siren thấp tần, bản năng sinh tồn
# ══════════════════════════════════════════════════════════════════════════════
def sfx_04():
    dur = 2.0
    tt  = t_(dur)
    # Warning pulse: 2 lần (nhịp tim tăng nhanh)
    wp = np.zeros(int(SR * dur))
    for pulse_t in [0.0, 0.45]:
        st  = int(pulse_t * SR)
        seg = np.arange(min(int(0.3*SR), len(wp)-st)) / SR
        wp[st:st+len(seg)] += (0.45*np.sin(2*np.pi*80*seg) +
                                0.20*np.sin(2*np.pi*160*seg)) * np.exp(-6*seg)
    # Dark brass — Dm ominous
    brass = (0.18 * np.sin(2*np.pi*146.8*tt) +
             0.12 * np.sin(2*np.pi*174.6*tt)) * adsr(dur, 0.05, 0.4, 0.3, 0.5)
    # High frequency alert shimmer
    alert = np.sin(2*np.pi*6000*tt) * np.exp(-12*tt) * 0.07
    sig   = wp + brass + alert
    sig   = reverb(sig, 0.12, 0.50, 5)
    sig[-int(0.3*SR):] *= np.linspace(1, 0, int(0.3*SR))
    save('sfx_04_threat_detected.wav', stereo(norm(sig), 14), "Mối đe dọa được nhận diện")


# ══════════════════════════════════════════════════════════════════════════════
# 5. sfx_05_cortisol_surge — 4s
#    Cortisol tràn vào hệ thống — McGaugh 1987
#    Cảm giác: dâng trào chậm, toàn thân, không thể chặn
# ══════════════════════════════════════════════════════════════════════════════
def sfx_05():
    dur = 4.0
    tt  = t_(dur)
    # Slow surge: riser từ 40Hz → 140Hz trong 3s
    f_surge = 40 + 100 * (tt / 3) ** 1.5
    f_surge = np.clip(f_surge, 40, 140)
    p_surge = 2*np.pi * np.cumsum(f_surge) / SR
    surge   = np.sin(p_surge) * adsr(dur, 0.8, 0.5, 0.6, 1.0) * 0.40
    # Am chord pad (stress response)
    pad = ((0.14 * np.sin(2*np.pi*220.0*tt) +
            0.10 * np.sin(2*np.pi*261.6*tt) +
            0.07 * np.sin(2*np.pi*329.6*tt)) *
           adsr(dur, 1.0, 0.5, 0.5, 1.0))
    # Sub rumble (adrenaline body response)
    rumble = lp(noise(dur), 60) * 0.05
    sig    = surge + pad + rumble
    sig    = reverb(sig, 0.20, 0.60, 6)
    sig[-int(1.0*SR):] *= np.linspace(1, 0, int(1.0*SR))
    save('sfx_05_cortisol_surge.wav', stereo(norm(sig), 16), "Cortisol dâng trào · stress hormone")


# ══════════════════════════════════════════════════════════════════════════════
# 6. sfx_06_memory_engrave — 3s
#    Ký ức được khắc sâu vào hippocampus (McGaugh effect)
#    Cảm giác: kim loại chạm đá, vĩnh viễn, không thể xóa
# ══════════════════════════════════════════════════════════════════════════════
def sfx_06():
    dur = 3.0
    tt  = t_(dur)
    # Metallic chisel strike — sắc bén
    strike_t = np.arange(int(0.15 * SR)) / SR
    strike   = (np.sin(2*np.pi*1200*strike_t) *
                np.sin(2*np.pi*1847*strike_t) *
                np.exp(-18*strike_t) * 0.65)
    sig = np.zeros(int(SR * dur))
    sig[:len(strike)] = strike
    # Stone resonance — tiếng đá vang lên sau
    resonance = (np.sin(2*np.pi*280*tt) + np.sin(2*np.pi*420*tt)) * np.exp(-2*tt) * 0.20
    # Memory encode ping — khoa học, chính xác
    ping = (np.sin(2*np.pi*1047*tt) * np.exp(-7*tt) * 0.12 +
            np.sin(2*np.pi*1319*tt) * np.exp(-9*tt) * 0.08)
    sig = sig + resonance + ping
    sig = reverb(sig, 0.22, 0.55, 5)
    sig[-int(0.5*SR):] *= np.linspace(1, 0, int(0.5*SR))
    save('sfx_06_memory_engrave.wav', stereo(norm(sig), 10), "Khắc sâu ký ức · hippocampus")


# ══════════════════════════════════════════════════════════════════════════════
# 7. sfx_07_zeigarnik_loop — 3.5s
#    Vòng lặp Zeigarnik — nhiệm vụ chưa hoàn thành
#    Cảm giác: bị kéo trở lại mãi, như file chưa đóng được
# ══════════════════════════════════════════════════════════════════════════════
def sfx_07():
    dur = 3.5
    # Ostinato 3 nốt lặp lại — E-D-C# (lẩn quẩn, không giải quyết được)
    n    = int(SR * dur)
    loop = np.zeros(n)
    step = int(0.6 * SR)
    notes = [329.6, 293.7, 277.2]
    for i in range(6):
        nf  = notes[i % 3]
        st  = i * step
        seg = np.arange(min(int(0.35*SR), n-st)) / SR
        if st >= n: break
        loop[st:st+len(seg)] += np.sin(2*np.pi*nf*seg) * np.exp(-4*seg) * 0.35
    # Unresolved tension pad — tritone F-B
    tt  = t_(dur)
    pad = (0.10*np.sin(2*np.pi*174.6*tt) +
           0.08*np.sin(2*np.pi*246.9*tt))
    pad *= adsr(dur, 0.3, 0.5, 0.6, 0.7)
    # "Open door" wind — cảm giác hở, chưa đóng
    wind = lp(noise(dur), 300) * 0.035
    sig  = loop + pad + wind
    sig  = reverb(sig, 0.25, 0.60, 6)
    sig[-int(0.8*SR):] *= np.linspace(1, 0, int(0.8*SR))
    save('sfx_07_zeigarnik_loop.wav', stereo(norm(sig), 18), "Vòng lặp Zeigarnik · ám ảnh")


# ══════════════════════════════════════════════════════════════════════════════
# 8. sfx_08_ratio_shock — 2s
#    Con số 4-5:1 xuất hiện — pattern interrupt 2
#    Cảm giác: gây sốc, bàng hoàng, số liệu khó tin
# ══════════════════════════════════════════════════════════════════════════════
def sfx_08():
    dur = 2.0
    tt  = t_(dur)
    # Impact hit — bật mạnh
    hit_t = np.arange(int(0.08*SR)) / SR
    hit   = (np.sin(2*np.pi*110*hit_t) * np.exp(-20*hit_t) * 0.55 +
             np.sin(2*np.pi*220*hit_t) * np.exp(-30*hit_t) * 0.30)
    sig   = np.zeros(int(SR * dur))
    sig[:len(hit)] = hit
    # Dark brass stab
    brass = ((0.20*np.sin(2*np.pi*138.6*tt) +
              0.15*np.sin(2*np.pi*185.0*tt)) *
             adsr(dur, 0.02, 0.3, 0.2, 0.6))
    # High crack — shock effect
    crack = np.random.uniform(-1,1,int(0.03*SR)) * 0.45
    crack = lp(np.concatenate([crack, np.zeros(int(SR*dur)-len(crack))]), 5000)
    sig   = sig + brass + crack
    sig   = reverb(sig, 0.15, 0.50, 4)
    sig[-int(0.3*SR):] *= np.linspace(1, 0, int(0.3*SR))
    save('sfx_08_ratio_shock.wav', stereo(norm(sig), 12), "Con số 4:1 · pattern interrupt 2")


# ══════════════════════════════════════════════════════════════════════════════
# 9. sfx_09_schema_click — 1.5s
#    Khuôn nhận thức schema khớp vào chỗ cũ
#    Cảm giác: như tìm thấy bằng chứng, "ừ thấy chưa"
# ══════════════════════════════════════════════════════════════════════════════
def sfx_09():
    dur = 1.5
    tt  = t_(dur)
    # Mechanical click — like a file snapping into place
    click_t = np.arange(int(0.06*SR)) / SR
    click   = (np.sin(2*np.pi*900*click_t) * np.exp(-40*click_t) * 0.45 +
               np.sin(2*np.pi*600*click_t) * np.exp(-50*click_t) * 0.25)
    sig = np.zeros(int(SR * dur))
    sig[:len(click)] = click
    # Minor resolution chord — không ổn, nhưng "quen"
    chord = ((0.12*np.sin(2*np.pi*220.0*tt) +
              0.08*np.sin(2*np.pi*261.6*tt)) *
             adsr(dur, 0.05, 0.4, 0.3, 0.5))
    sig = sig + chord
    sig = reverb(sig, 0.08, 0.30, 3)
    sig[-int(0.3*SR):] *= np.linspace(1, 0, int(0.3*SR))
    save('sfx_09_schema_click.wav', stereo(norm(sig), 10), "Schema khớp · confirmation bias")


# ══════════════════════════════════════════════════════════════════════════════
# 10. sfx_10_pattern_interrupt — 1s
#     Pattern interrupt — kéo người xem quay lại
#     Cảm giác: bất ngờ nhẹ, "khoan đã", wake-up call
# ══════════════════════════════════════════════════════════════════════════════
def sfx_10():
    dur = 1.0
    tt  = t_(dur)
    # Short whoosh upward
    f_w = 200 + 800 * (tt / 0.3)
    f_w = np.clip(f_w, 200, 1000)
    p_w = 2*np.pi * np.cumsum(f_w) / SR
    whoosh = np.sin(p_w) * adsr(dur, 0.05, 0.2, 0.1, 0.6) * 0.30
    # Clean ping arrival
    ping = (np.sin(2*np.pi*1319*tt) * np.exp(-8*tt) * 0.35 +
            np.sin(2*np.pi*1760*tt) * np.exp(-10*tt) * 0.20)
    sig  = whoosh + ping
    sig  = reverb(sig, 0.06, 0.25, 2)
    sig[-int(0.2*SR):] *= np.linspace(1, 0, int(0.2*SR))
    save('sfx_10_pattern_interrupt.wav', stereo(norm(sig), 8), "Pattern interrupt · wake-up call")


# ══════════════════════════════════════════════════════════════════════════════
# 11. sfx_11_neuroplasticity — 4s
#     Đường thần kinh mới hình thành — neuroplasticity
#     Cảm giác: ánh sáng mới, tia sáng, hy vọng, thay đổi được
# ══════════════════════════════════════════════════════════════════════════════
def sfx_11():
    dur = 4.0
    tt  = t_(dur)
    # Bright rising — từ dark Am sang light D major
    f_r = 220 * (1 + 0.5 * np.clip(tt / 2, 0, 1))
    p_r = 2*np.pi * np.cumsum(f_r) / SR
    rise = np.sin(p_r) * adsr(dur, 1.0, 0.5, 0.5, 1.0) * 0.25
    # D major chord bloom (146.8-184.9-220-246.9)
    dm  = ((0.18*np.sin(2*np.pi*146.8*tt) +
            0.13*np.sin(2*np.pi*184.9*tt) +
            0.10*np.sin(2*np.pi*220.0*tt) +
            0.07*np.sin(2*np.pi*246.9*tt)) *
           adsr(dur, 1.5, 0.5, 0.6, 1.0))
    # Crystal high — synaptic spark (2093Hz)
    crystal = np.sin(2*np.pi*2093*tt) * np.exp(-2*tt) * 0.08
    # Second spark tại 1.5s — new pathway forming
    sp2_t = tt - 1.5
    sp2_t = np.where(sp2_t > 0, sp2_t, 0)
    crystal2 = np.sin(2*np.pi*2637*sp2_t) * np.exp(-3*sp2_t) * 0.06
    # Sub warmth
    sub = np.sin(2*np.pi*73.4*tt) * np.exp(-tt/4) * 0.12
    sig = rise + dm + crystal + crystal2 + sub
    sig = reverb(sig, 0.25, 0.55, 5)
    sig[-int(1.2*SR):] *= np.linspace(1, 0, int(1.2*SR))
    save('sfx_11_neuroplasticity.wav', stereo(norm(sig), 20), "Neuroplasticity · ánh sáng hy vọng")


# ══════════════════════════════════════════════════════════════════════════════
# 12. sfx_12_warm_closing — 5s
#     Kết ấm — tự nói chuyện với bản thân, bài học
#     Cảm giác: nhẹ nhàng, ấm áp, đặt xuống được rồi
# ══════════════════════════════════════════════════════════════════════════════
def sfx_12():
    dur = 5.0
    tt  = t_(dur)
    # G major warm drone (196-246.9-293.7)
    warm = ((0.22*np.sin(2*np.pi*196.0*tt) +
             0.16*np.sin(2*np.pi*246.9*tt) +
             0.11*np.sin(2*np.pi*293.7*tt) +
             0.06*np.sin(2*np.pi*392.0*tt)) *
            adsr(dur, 1.5, 0.5, 0.7, 1.5))
    # Gentle LFO
    lfo = 1 + 0.04 * np.sin(2*np.pi*0.2*tt)
    warm *= lfo
    # High gentle bell — G5=784Hz, like a soft wind chime
    bell1 = (np.sin(2*np.pi*784.0*tt) * np.exp(-1.5*tt) * 0.07 +
             np.sin(2*np.pi*1046.5*tt) * np.exp(-2.0*tt) * 0.05)
    # Sub warmth
    sub = np.sin(2*np.pi*98.0*tt) * adsr(dur, 2.0, 0.5, 0.5, 2.0) * 0.15
    # Soft ambient texture
    amb = lp(noise(dur), 200) * 0.025
    sig = warm + bell1 + sub + amb
    sig = reverb(sig, 0.35, 0.65, 7)
    sig[-int(2.0*SR):] *= np.linspace(1, 0, int(2.0*SR))
    save('sfx_12_warm_closing.wav', stereo(norm(sig), 22), "Kết ấm · bài học · đặt xuống")


# ── SFX Config JSON ───────────────────────────────────────────────────────────
def save_config():
    config = {
        "sfx_01_bedroom_night":    {"file": "sfx_01_bedroom_night.wav",    "volume": 0.45, "trigger": "Mở đầu · phòng ngủ tối"},
        "sfx_02_question_rise":    {"file": "sfx_02_question_rise.wav",    "volume": 0.38, "trigger": "Câu hỏi hook xuất hiện"},
        "sfx_03_amygdala_fire":    {"file": "sfx_03_amygdala_fire.wav",    "volume": 0.60, "trigger": "Amygdala khai hỏa (180ms)"},
        "sfx_04_threat_detected":  {"file": "sfx_04_threat_detected.wav",  "volume": 0.50, "trigger": "Não nhận diện mối đe dọa"},
        "sfx_05_cortisol_surge":   {"file": "sfx_05_cortisol_surge.wav",   "volume": 0.42, "trigger": "Cortisol dâng trào"},
        "sfx_06_memory_engrave":   {"file": "sfx_06_memory_engrave.wav",   "volume": 0.48, "trigger": "Ký ức khắc sâu · hippocampus"},
        "sfx_07_zeigarnik_loop":   {"file": "sfx_07_zeigarnik_loop.wav",   "volume": 0.40, "trigger": "Vòng lặp Zeigarnik"},
        "sfx_08_ratio_shock":      {"file": "sfx_08_ratio_shock.wav",      "volume": 0.62, "trigger": "Con số 4-5:1 gây sốc"},
        "sfx_09_schema_click":     {"file": "sfx_09_schema_click.wav",     "volume": 0.35, "trigger": "Schema khớp confirmation bias"},
        "sfx_10_pattern_interrupt":{"file": "sfx_10_pattern_interrupt.wav","volume": 0.42, "trigger": "Pattern interrupt · 3 lần"},
        "sfx_11_neuroplasticity":  {"file": "sfx_11_neuroplasticity.wav",  "volume": 0.50, "trigger": "Neuroplasticity · hy vọng"},
        "sfx_12_warm_closing":     {"file": "sfx_12_warm_closing.wav",     "volume": 0.45, "trigger": "Kết ấm · bài học"},
        "backgroundMusic":         {"file": "background-music.wav",        "volume": 0.14, "trigger": "Xuyên suốt video"},
    }
    path = os.path.join(DIR, 'sfx-config.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"\n  sfx-config.json → {path}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 65)
    print("  12 SFX CINEMATIC — LDN — Negativity Bias Video")
    print("=" * 65)
    sfx_01()
    sfx_02()
    sfx_03()
    sfx_04()
    sfx_05()
    sfx_06()
    sfx_07()
    sfx_08()
    sfx_09()
    sfx_10()
    sfx_11()
    sfx_12()
    save_config()
    print("\n" + "=" * 65)
    print("  HOÀN THÀNH! 12 SFX + config đã lưu vào public/sfx/")
    print("=" * 65)

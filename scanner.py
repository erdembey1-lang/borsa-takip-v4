import yfinance as yf
import pandas as pd
import numpy as np

from datetime import datetime, timedelta

from hisseler import bist_hisselerini_getir


# ============================================================
# GÜNLÜK V4 TARAMA
# ============================================================

MAX_ONERI = 4

VERI_GUNU = 420

HEDEF_ATR = 3.0

SONUC_DOSYASI = "gunluk_sinyaller_v4.csv"


# ============================================================
# VERİ
# ============================================================

def veri_al(sembol):

    try:

        bugun = datetime.now()

        baslangic = (
            bugun -
            timedelta(days=VERI_GUNU)
        )

        data = yf.download(
            sembol,
            start=baslangic.strftime("%Y-%m-%d"),
            end=(bugun + timedelta(days=1)).strftime("%Y-%m-%d"),
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        gerekli = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for kolon in gerekli:
            if kolon not in data.columns:
                return None

        data = data[gerekli].copy()

        for kolon in gerekli:
            data[kolon] = pd.to_numeric(
                data[kolon],
                errors="coerce"
            )

        data = data.dropna()

        if len(data) < 220:
            return None

        return data

    except Exception as e:

        print(
            f"Hata {sembol}: {e}"
        )

        return None


# ============================================================
# TEKNİK GÖSTERGELER
# ============================================================

def gostergeleri_hesapla(data):

    data = data.copy()

    close = data["Close"]
    high = data["High"]
    low = data["Low"]
    volume = data["Volume"]

    # RSI
    delta = close.diff()

    kazanc = delta.clip(lower=0)
    kayip = -delta.clip(upper=0)

    ort_kazanc = (
        kazanc.rolling(14).mean()
    )

    ort_kayip = (
        kayip.rolling(14).mean()
    )

    rs = (
        ort_kazanc /
        ort_kayip.replace(0, np.nan)
    )

    data["RSI"] = (
        100 -
        (100 / (1 + rs))
    )

    # Trend
    data["EMA20"] = (
        close
        .ewm(
            span=20,
            adjust=False
        )
        .mean()
    )

    data["EMA50"] = (
        close
        .ewm(
            span=50,
            adjust=False
        )
        .mean()
    )

    data["SMA200"] = (
        close
        .rolling(200)
        .mean()
    )

    # ATR
    previous_close = close.shift()

    high_low = (
        high - low
    )

    high_close = (
        high - previous_close
    ).abs()

    low_close = (
        low - previous_close
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    data["ATR"] = (
        true_range
        .rolling(14)
        .mean()
    )

    # Hacim
    data["VolumeAvg20"] = (
        volume
        .rolling(20)
        .mean()
    )

    # Momentum
    data["Momentum20"] = (
        close
        .pct_change(20)
        * 100
    )

    data["Momentum5"] = (
        close
        .pct_change(5)
        * 100
    )

    # Breakout
    data["Previous20High"] = (
        high
        .rolling(20)
        .max()
        .shift(1)
    )

    return data


# ============================================================
# TEK HİSSE PUANLAMA
# ============================================================

def analiz_et(sembol):

    data = veri_al(sembol)

    if data is None:
        return None

    data = gostergeleri_hesapla(data)

    if data is None:
        return None

    # SON MEVCUT BIST İŞLEM GÜNÜ
    index = len(data) - 1

    row = data.iloc[index]

    try:

        fiyat = float(row["Close"])
        rsi = float(row["RSI"])
        ema20 = float(row["EMA20"])
        ema50 = float(row["EMA50"])
        sma200 = float(row["SMA200"])
        atr = float(row["ATR"])
        hacim = float(row["Volume"])
        hacim_ort = float(row["VolumeAvg20"])
        momentum20 = float(row["Momentum20"])
        momentum5 = float(row["Momentum5"])
        onceki_zirve = float(row["Previous20High"])

    except Exception:

        return None

    degerler = [
        fiyat,
        rsi,
        ema20,
        ema50,
        sma200,
        atr,
        hacim,
        hacim_ort,
        momentum20,
        momentum5,
        onceki_zirve
    ]

    if any(pd.isna(x) for x in degerler):
        return None

    if fiyat <= 0 or atr <= 0 or hacim_ort <= 0:
        return None

    hacim_orani = (
        hacim /
        hacim_ort
    )

    atr_yuzde = (
        atr /
        fiyat
    ) * 100

    breakout = (
        fiyat >
        onceki_zirve
    )

    # ========================================================
    # PUAN
    # ========================================================

    skor = 0

    # Momentum 20
    if momentum20 >= 20:
        skor += 25
    elif momentum20 >= 15:
        skor += 20
    elif momentum20 >= 10:
        skor += 15
    elif momentum20 >= 5:
        skor += 10
    elif momentum20 > 0:
        skor += 5

    # Hacim
    if hacim_orani >= 3:
        skor += 20
    elif hacim_orani >= 2:
        skor += 17
    elif hacim_orani >= 1.5:
        skor += 13
    elif hacim_orani >= 1.2:
        skor += 8

    # Trend
    if ema20 > ema50:
        skor += 8

    if fiyat > ema20:
        skor += 4

    if fiyat > sma200:
        skor += 3

    # Breakout
    if breakout:
        skor += 15

    # RSI
    if 55 <= rsi <= 68:
        skor += 10
    elif 50 <= rsi < 55:
        skor += 7
    elif 68 < rsi <= 72:
        skor += 5
    elif 72 < rsi <= 80:
        skor += 2

    # Momentum 5
    if momentum5 >= 8:
        skor += 10
    elif momentum5 >= 5:
        skor += 8
    elif momentum5 >= 2:
        skor += 5
    elif momentum5 > 0:
        skor += 2

    # Volatilite
    if 3 <= atr_yuzde <= 6:
        skor += 5
    elif 2 <= atr_yuzde < 3:
        skor += 3

    # ========================================================
    # DURUM
    # ========================================================

    pozitif_trend = (
        fiyat > ema20
        and
        ema20 > ema50
        and
        fiyat > sma200
    )

    momentum_pozitif = (
        momentum20 > 0
        and
        momentum5 > 0
    )

    hacim_pozitif = (
        hacim_orani >= 1.2
    )

    if (
        pozitif_trend
        and
        momentum_pozitif
        and
        hacim_pozitif
    ):

        durum = "GÜÇLÜ ADAY"

    elif (
        momentum_pozitif
        or
        breakout
    ):

        durum = "İZLE"

    else:

        durum = "ZAYIF"


    # ========================================================
    # HEDEF
    # ========================================================

    hedef = (
        fiyat +
        atr * HEDEF_ATR
    )

    hedef_getiri = (
        (
            hedef /
            fiyat
        ) - 1
    ) * 100


    return {

        "sembol": sembol,

        "tarih": data.index[-1].strftime(
            "%Y-%m-%d"
        ),

        "fiyat": fiyat,

        "skor": skor,

        "durum": durum,

        "rsi": rsi,

        "hacim_orani": hacim_orani,

        "momentum20": momentum20,

        "momentum5": momentum5,

        "atr_yuzde": atr_yuzde,

        "breakout": breakout,

        "hedef": hedef,

        "hedef_getiri": hedef_getiri

    }


# ============================================================
# TARAMA
# ============================================================

def tara():

    print()

    print("=" * 70)
    print("📡 V4 GÜNLÜK BIST TARAMASI")
    print("=" * 70)

    hisseler = (
        bist_hisselerini_getir()
    )

    sonuclar = []

    print(
        f"Toplam hisse: {len(hisseler)}"
    )

    print()


    for sira, sembol in enumerate(
        hisseler,
        start=1
    ):

        print(
            f"[{sira}/{len(hisseler)}] "
            f"{sembol}"
        )

        sonuc = analiz_et(
            sembol
        )

        if sonuc is not None:
            sonuclar.append(
                sonuc
            )


    if not sonuclar:

        print(
            "❌ Veri alınamadı."
        )

        return


    df = pd.DataFrame(
        sonuclar
    )


    # ========================================================
    # EN İYİLERİ SEÇ
    # ========================================================

    df = df.sort_values(
        by=[
            "skor",
            "momentum20",
            "hacim_orani"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )


    oneriler = df.head(
        MAX_ONERI
    ).copy()


    # ========================================================
    # SONUÇ
    # ========================================================

    print()

    print("=" * 70)
    print("🏆 BUGÜNÜN EN İYİ 4 V4 ADAYI")
    print("=" * 70)

    for sira, (_, hisse) in enumerate(
        oneriler.iterrows(),
        start=1
    ):

        print()

        print(
            f"{sira}. {hisse['sembol']} "
            f"→ {hisse['durum']}"
        )

        print("-" * 55)

        print(
            f"Skor          : "
            f"{hisse['skor']:.0f}/100"
        )

        print(
            f"Fiyat         : "
            f"{hisse['fiyat']:.2f} TL"
        )

        print(
            f"RSI           : "
            f"{hisse['rsi']:.2f}"
        )

        print(
            f"Momentum20    : "
            f"%{hisse['momentum20']:.2f}"
        )

        print(
            f"Momentum5     : "
            f"%{hisse['momentum5']:.2f}"
        )

        print(
            f"Hacim         : "
            f"{hisse['hacim_orani']:.2f}x"
        )

        print(
            f"ATR           : "
            f"%{hisse['atr_yuzde']:.2f}"
        )

        print(
            f"Breakout      : "
            f"{'EVET' if hisse['breakout'] else 'HAYIR'}"
        )

        print(
            f"3 ATR Hedef   : "
            f"{hisse['hedef']:.2f} TL"
        )

        print(
            f"Hedef Getiri  : "
            f"%{hisse['hedef_getiri']:.2f}"
        )


    # ========================================================
    # CSV
    # ========================================================

    oneriler.to_csv(
        "gunluk_sinyaller_v4.csv",
        index=False,
        encoding="utf-8-sig"
    )


    print()

    print("=" * 70)

    print(
        "💾 gunluk_sinyaller_v4.csv"
    )

    print("=" * 70)


# ============================================================
# ÇALIŞTIR
# ============================================================

def tara_web():

    hisseler = bist_hisselerini_getir()

    sonuclar = []

    for sembol in hisseler:

        sonuc = analiz_et(sembol)

        if sonuc is not None:
            sonuclar.append(sonuc)

    if not sonuclar:
        return []

    df = pd.DataFrame(sonuclar)

    df = df.sort_values(
        by=[
            "skor",
            "momentum20",
            "hacim_orani"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    oneriler = (
        df.head(4)
        .copy()
    )

    oneriler.to_csv(
        "gunluk_sinyaller_v4.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return (
        oneriler
        .to_dict("records")
    )

if __name__ == "__main__":

    tara()
from flask import Flask, render_template_string, request
from scanner import tara_web

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Borsa Takip V4</title>

    <style>

        * {
            box-sizing: border-box;
        }

        html,
        body {
            margin: 0;
            padding: 0;
            width: 100%;
            min-height: 100%;
        }

        body {
            font-family:
                Arial,
                Helvetica,
                sans-serif;

            background: #f3f4f6;
            color: #111827;

            overflow-x: hidden;
        }

        .container {

            width: 100%;
            max-width: 720px;

            margin: 0 auto;

            padding:
                16px 12px 40px;
        }

        .header {

            text-align: center;

            padding:
                10px 0 18px;
        }

        .logo {

            font-size: 42px;

            margin-bottom: 5px;
        }

        .title {

            font-size: 30px;
            font-weight: 800;

            margin: 0;
        }

        .subtitle {

            color: #6b7280;

            font-size: 15px;

            margin-top: 7px;
        }

        .scan-form {

            margin-bottom: 18px;
        }

        .scan-button {

            width: 100%;

            border: none;
            border-radius: 14px;

            padding: 17px;

            background: #111827;
            color: white;

            font-size: 20px;
            font-weight: 700;

            cursor: pointer;
        }

        .scan-button:active {

            transform: scale(.99);
        }

        .info {

            background: white;

            border-radius: 14px;

            padding: 14px 15px;

            margin-bottom: 16px;

            color: #6b7280;

            font-size: 14px;

            text-align: center;
        }

        .card {

            width: 100%;

            background: white;

            border-radius: 16px;

            padding: 18px 16px;

            margin-bottom: 15px;

            box-shadow:
                0 4px 16px rgba(0,0,0,.07);

            overflow: hidden;
        }

        .rank {

            color: #6b7280;

            font-size: 13px;

            margin-bottom: 5px;
        }

        .symbol {

            font-size: 26px;

            font-weight: 800;

            word-break: break-word;

            margin-bottom: 7px;
        }

        .status {

            display: inline-block;

            padding:
                6px 10px;

            border-radius: 999px;

            background: #ecfdf5;

            color: #047857;

            font-size: 12px;

            font-weight: 700;

            margin-bottom: 14px;
        }

        .score {

            font-size: 21px;

            font-weight: 800;

            margin-bottom: 12px;
        }

        .row {

            width: 100%;

            display: flex;

            justify-content:
                space-between;

            align-items: center;

            gap: 12px;

            padding: 9px 0;

            border-bottom:
                1px solid #eeeeee;
        }

        .row:last-child {

            border-bottom: none;
        }

        .label {

            color: #6b7280;

            font-size: 14px;

            flex: 1;
        }

        .value {

            font-size: 14px;

            font-weight: 700;

            text-align: right;

            white-space: nowrap;
        }

        .target {

            margin-top: 12px;

            padding: 12px;

            border-radius: 12px;

            background: #f0fdf4;

            color: #166534;
        }

        .empty {

            background: white;

            border-radius: 16px;

            padding: 30px 18px;

            text-align: center;

            color: #6b7280;
        }

        .footer {

            text-align: center;

            color: #9ca3af;

            font-size: 12px;

            margin-top: 24px;
        }


        @media (max-width: 480px) {

            .container {

                padding:
                    12px 10px 30px;
            }

            .logo {

                font-size: 34px;
            }

            .title {

                font-size: 25px;
            }

            .subtitle {

                font-size: 14px;
            }

            .scan-button {

                font-size: 18px;

                padding: 15px;
            }

            .card {

                padding: 16px 13px;
            }

            .symbol {

                font-size: 23px;
            }

            .row {

                padding: 8px 0;
            }
        }

    </style>

</head>


<body>

<div class="container">

    <div class="header">

        <div class="logo">
            📈
        </div>

        <h1 class="title">
            Borsa Takip V4
        </h1>

        <div class="subtitle">
            Günlük 4 hisse taraması
        </div>

    </div>


    <form
        method="POST"
        class="scan-form"
    >

        <button
            type="submit"
            class="scan-button"
        >
            🔎 TARA
        </button>

    </form>


    {% if searched %}

        <div class="info">

            Son tarama tamamlandı.

            En yüksek puanlı
            4 aday aşağıda gösteriliyor.

        </div>

    {% endif %}


    {% if results %}

        {% for item in results %}

            <div class="card">

                <div class="rank">

                    #{{ loop.index }}

                </div>


                <div class="symbol">

                    {{ item.sembol }}

                </div>


                <div class="status">

                    {{ item.get("durum", "ADAY") }}

                </div>


                <div class="score">

                    Skor:
                    {{ item.skor }}/100

                </div>


                <div class="row">

                    <span class="label">
                        Fiyat
                    </span>

                    <span class="value">

                        {{ "%.2f"|format(item.fiyat) }}
                        TL

                    </span>

                </div>


                <div class="row">

                    <span class="label">
                        RSI
                    </span>

                    <span class="value">

                        {{ "%.2f"|format(item.rsi) }}

                    </span>

                </div>


                <div class="row">

                    <span class="label">
                        Momentum 20G
                    </span>

                    <span class="value">

                        %{{ "%.2f"|format(item.momentum20) }}

                    </span>

                </div>


                <div class="row">

                    <span class="label">
                        Momentum 5G
                    </span>

                    <span class="value">

                        %{{ "%.2f"|format(item.momentum5) }}

                    </span>

                </div>


                <div class="row">

                    <span class="label">
                        Hacim
                    </span>

                    <span class="value">

                        {{ "%.2f"|format(item.hacim_orani) }}x

                    </span>

                </div>


                <div class="row">

                    <span class="label">
                        ATR
                    </span>

                    <span class="value">

                        %{{ "%.2f"|format(item.atr_yuzde) }}

                    </span>

                </div>


                <div class="row">

                    <span class="label">
                        Breakout
                    </span>

                    <span class="value">

                        {{ "EVET" if item.breakout else "HAYIR" }}

                    </span>

                </div>


                <div class="target">

                    <div class="row">

                        <span class="label">
                            3 ATR Hedef
                        </span>

                        <span class="value">

                            {{ "%.2f"|format(item.hedef) }}
                            TL

                        </span>

                    </div>


                    <div class="row">

                        <span class="label">
                            Hedef Getiri
                        </span>

                        <span class="value">

                            %{{ "%.2f"|format(item.hedef_getiri) }}

                        </span>

                    </div>

                </div>

            </div>

        {% endfor %}


    {% elif searched %}

        <div class="empty">

            Bugün veri alınamadı veya aday oluşmadı.

        </div>

    {% endif %}


    <div class="footer">

        Borsa Takip V4

    </div>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def ana_sayfa():

    results = []

    searched = False

    if request.method == "POST":

        searched = True

        try:

            results = tara_web()

        except Exception as e:

            print(
                f"Tarama hatası: {e}"
            )

            results = []

    return render_template_string(
        HTML,
        results=results,
        searched=searched
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
from datetime import datetime
from sklearn.linear_model import LinearRegression
from app import db
from app.models import Resident, PopulationHistory

def sync_current_year():
    tahun_sekarang = datetime.now().year
    jumlah_penduduk = Resident.query.count()
    history = PopulationHistory.query.filter_by(
        tahun=tahun_sekarang
    ).first()

    if history:
        history.jumlah = jumlah_penduduk
    else:
        history = PopulationHistory(
            tahun=tahun_sekarang,
            jumlah=jumlah_penduduk
        )
        db.session.add(history)
    db.session.commit()

def predict_next_year():
    sync_current_year()
    data = PopulationHistory.query.order_by(
        PopulationHistory.tahun
    ).all()

    if len(data) < 2:
        return {
            "prediction": None,
            "message": "Data riwayat minimal 2 tahun diperlukan."
        }

    X = [
        [item.tahun]
        for item in data
    ]

    y = [
        item.jumlah
        for item in data
    ]

    model = LinearRegression()
    model.fit(X, y)

    tahun_berikutnya = datetime.now().year + 1

    prediction = model.predict(
        [[tahun_berikutnya]]
    )[0]

    prediction = max(
        0,
        round(prediction)
    )

    return {
        "prediction": prediction,
        "tahun": tahun_berikutnya,
        "message": "Prediksi berhasil."
    }
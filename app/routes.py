import os
import csv
import io
import uuid

from werkzeug.utils import secure_filename
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    send_from_directory,
    url_for,
    flash,
    send_file,
    current_app
)

from flask_login import (
    login_required
)
from werkzeug.utils import secure_filename
from app import db

from app.models import (
    Resident,
    PopulationHistory,
    Activity,
    ActivityImage
)

from app.ml import (
    predict_next_year,
    sync_current_year
)

main = Blueprint(
    "main",
    __name__
)

PENDIDIKAN_OPTIONS = [
    "Tidak ada",
    "SD",
    "SMP",
    "SMA/SMK",
    "Diploma",
    "Sarjana"
]

DUSUN_OPTIONS = [
    "Jatirejo",
    "Karajan"
]

JENIS_KELAMIN_OPTIONS = [
    "Laki-laki",
    "Perempuan"
]

@main.route("/")
def index():
    sync_current_year()

    total_penduduk = Resident.query.count()

    laki_laki = Resident.query.filter_by(
        jenis_kelamin="Laki-laki"
    ).count()

    perempuan = Resident.query.filter_by(
        jenis_kelamin="Perempuan"
    ).count()

    prediction = predict_next_year()
    history_chart = PopulationHistory.query.order_by(
        PopulationHistory.tahun.asc()
    ).all()

    history_years = [item.tahun for item in history_chart]
    history_counts = [item.jumlah for item in history_chart]

    activities = Activity.query.order_by(
        Activity.tanggal.desc()
    ).all()

    history = PopulationHistory.query.order_by(
        PopulationHistory.tahun.asc()
    ).all()

    return render_template(
        "index.html",
        total_penduduk=total_penduduk,
        laki_laki=laki_laki,
        perempuan=perempuan,
        prediction=prediction,
        activities=activities,
        history=history,
        history_years=history_years,
        history_counts=history_counts
    )

@main.route("/admin")
@login_required
def admin():
    sync_current_year()

    residents = Resident.query.order_by(
        Resident.nama.asc()
    ).all()

    total = Resident.query.count()

    laki_laki = Resident.query.filter_by(
        jenis_kelamin="Laki-laki"
    ).count()

    perempuan = Resident.query.filter_by(
        jenis_kelamin="Perempuan"
    ).count()

    return render_template(
        "admin/data_penduduk.html",
        residents=residents,
        total=total,
        laki_laki=laki_laki,
        perempuan=perempuan
    )

@main.route("/admin/tambah")
@login_required
def admin_tambah():
    return render_template(
        "admin/tambah_data.html",
        pendidikan_options=PENDIDIKAN_OPTIONS,
        dusun_options=DUSUN_OPTIONS,
        jenis_kelamin_options=JENIS_KELAMIN_OPTIONS
    )

@main.route(
    "/admin/resident/add",
    methods=["POST"]
)
@login_required
def add_resident():

    nik = request.form.get("nik", "").strip()
    nama = request.form.get("nama", "").strip()
    jenis_kelamin = request.form.get("jenis_kelamin", "").strip()
    dusun = request.form.get("dusun", "").strip()
    tanggal_lahir = request.form.get("tanggal_lahir", "").strip()
    pekerjaan = request.form.get("pekerjaan", "").strip()
    pendidikan = request.form.get("pendidikan", "").strip()

    if not nik.isdigit() or len(nik) != 16:
        flash(
            "NIK harus terdiri dari 16 digit.",
            "danger"
        )
        return redirect(url_for("main.admin_tambah"))

    if not nama:
        flash(
            "Nama wajib diisi.",
            "danger"
        )
        return redirect(url_for("main.admin_tambah"))

    if jenis_kelamin not in JENIS_KELAMIN_OPTIONS:
        flash(
            "Jenis kelamin tidak valid.",
            "danger"
        )
        return redirect(url_for("main.admin_tambah"))

    if dusun not in DUSUN_OPTIONS:
        flash(
            "Dusun tidak valid.",
            "danger"
        )
        return redirect(url_for("main.admin_tambah"))

    if pendidikan not in PENDIDIKAN_OPTIONS:
        flash(
            "Pendidikan tidak valid.",
            "danger"
        )
        return redirect(url_for("main.admin_tambah"))

    existing = Resident.query.filter_by(
        nik=nik
    ).first()

    if existing:
        flash(
            "NIK sudah terdaftar.",
            "danger"
        )
        return redirect(url_for("main.admin_tambah"))

    resident = Resident(
        nik=nik,
        nama=nama,
        jenis_kelamin=jenis_kelamin,
        dusun=dusun,
        tanggal_lahir=tanggal_lahir,
        pekerjaan=pekerjaan,
        pendidikan=pendidikan
    )

    db.session.add(resident)
    db.session.commit()

    flash(
        "Data penduduk berhasil ditambahkan.",
        "success"
    )

    return redirect(
        url_for("main.admin")
    )

@main.route("/admin/edit")
@login_required
def admin_edit():
    search = request.args.get("search", "").strip()

    residents = []

    if search:
        residents = Resident.query.filter(
            db.or_(
                Resident.nik.ilike(f"%{search}%"),
                Resident.nama.ilike(f"%{search}%")
            )
        ).order_by(Resident.nama.asc()).all()

    return render_template(
        "admin/edit_data.html",
        residents=residents,
        search=search,
        pendidikan_options=PENDIDIKAN_OPTIONS,
        dusun_options=DUSUN_OPTIONS,
        jenis_kelamin_options=JENIS_KELAMIN_OPTIONS
    )

@main.route(
    "/admin/resident/edit/<int:resident_id>",
    methods=["POST"]
)
@login_required
def edit_resident(resident_id):

    resident = Resident.query.get_or_404(resident_id)

    nik = request.form.get("nik", "").strip()
    nama = request.form.get("nama", "").strip()
    jenis_kelamin = request.form.get("jenis_kelamin", "").strip()
    dusun = request.form.get("dusun", "").strip()
    tanggal_lahir = request.form.get("tanggal_lahir", "").strip()
    pekerjaan = request.form.get("pekerjaan", "").strip()
    pendidikan = request.form.get("pendidikan", "").strip()

    if not nik.isdigit() or len(nik) != 16:
        flash("NIK harus terdiri dari 16 digit.", "danger")
        return redirect(url_for("main.admin_edit"))

    existing = Resident.query.filter(
        Resident.nik == nik,
        Resident.id != resident.id
    ).first()

    if existing:
        flash("NIK sudah digunakan oleh penduduk lain.", "danger")
        return redirect(url_for("main.admin_edit"))

    if not nama:
        flash("Nama wajib diisi.", "danger")
        return redirect(url_for("main.admin_edit"))

    if jenis_kelamin not in JENIS_KELAMIN_OPTIONS:
        flash("Jenis kelamin tidak valid.", "danger")
        return redirect(url_for("main.admin_edit"))

    if dusun not in DUSUN_OPTIONS:
        flash("Dusun tidak valid.", "danger")
        return redirect(url_for("main.admin_edit"))

    if pendidikan not in PENDIDIKAN_OPTIONS:
        flash("Pendidikan tidak valid.", "danger")
        return redirect(url_for("main.admin_edit"))

    resident.nik = nik
    resident.nama = nama
    resident.jenis_kelamin = jenis_kelamin
    resident.dusun = dusun
    resident.tanggal_lahir = tanggal_lahir
    resident.pekerjaan = pekerjaan
    resident.pendidikan = pendidikan

    db.session.commit()

    flash(
        "Data penduduk berhasil diperbarui.",
        "success"
    )

    return redirect(
        url_for("main.admin")
    )

@main.route("/admin/hapus")
@login_required
def admin_hapus():
    search = request.args.get("search", "").strip()

    residents = []

    if search:
        residents = Resident.query.filter(
            db.or_(
                Resident.nik.ilike(f"%{search}%"),
                Resident.nama.ilike(f"%{search}%")
            )
        ).order_by(Resident.nama.asc()).all()

    return render_template(
        "admin/hapus_data.html",
        residents=residents,
        search=search
    )

@main.route("/admin/resident/delete/<int:resident_id>", methods=["POST"])
@login_required
def delete_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)

    db.session.delete(resident)
    db.session.commit()

    flash("Data penduduk berhasil dihapus.", "success")
    return redirect(url_for("main.admin"))

@main.route("/admin/import")
@login_required
def admin_import():

    return render_template(
        "admin/import_csv.html"
    )

@main.route("/admin/import", methods=["GET", "POST"])
@login_required
def import_csv():
    if request.method == "GET":
        return render_template("admin/import_csv.html")

    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Silakan pilih file CSV.", "danger")
        return redirect(url_for("main.admin_import"))

    if not file.filename.lower().endswith(".csv"):
        flash("File harus berformat CSV.", "danger")
        return redirect(url_for("main.admin_import"))

    try:
        stream = io.StringIO(
            file.stream.read().decode("utf-8-sig"),
            newline=""
        )

        reader = csv.DictReader(stream)

        required_columns = [
            "nik",
            "nama",
            "jenis_kelamin",
            "dusun",
            "tanggal_lahir",
            "pekerjaan",
            "pendidikan_terakhir"
        ]

        if not reader.fieldnames:
            flash("File CSV tidak memiliki header.", "danger")
            return redirect(url_for("main.admin_import"))

        missing_columns = [
            column
            for column in required_columns
            if column not in reader.fieldnames
        ]

        if missing_columns:
            flash(
                "Kolom CSV tidak lengkap: "
                + ", ".join(missing_columns),
                "danger"
            )
            return redirect(url_for("main.admin_import"))

        added = 0
        skipped = 0

        for row in reader:
            nik = row.get("nik", "").strip()
            nama = row.get("nama", "").strip()
            jenis_kelamin = row.get("jenis_kelamin", "").strip()
            dusun = row.get("dusun", "").strip()
            tanggal_lahir = row.get("tanggal_lahir", "").strip()
            pekerjaan = row.get("pekerjaan", "").strip()
            pendidikan = row.get("pendidikan_terakhir", "").strip()

            # Lewati data yang tidak valid
            if not nik.isdigit() or len(nik) != 16:
                skipped += 1
                continue

            if not nama:
                skipped += 1
                continue

            if jenis_kelamin not in JENIS_KELAMIN_OPTIONS:
                skipped += 1
                continue

            if dusun not in DUSUN_OPTIONS:
                skipped += 1
                continue

            if pendidikan not in PENDIDIKAN_OPTIONS:
                skipped += 1
                continue

            existing = Resident.query.filter_by(nik=nik).first()

            if existing:
                skipped += 1
                continue

            resident = Resident(
                nik=nik,
                nama=nama,
                jenis_kelamin=jenis_kelamin,
                dusun=dusun,
                tanggal_lahir=tanggal_lahir,
                pekerjaan=pekerjaan,
                pendidikan=pendidikan
            )

            db.session.add(resident)
            added += 1

        db.session.commit()

        flash(
            f"Import selesai. {added} data ditambahkan, "
            f"{skipped} data dilewati.",
            "success"
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Gagal membaca file CSV: {e}", "danger")

    return redirect(url_for("main.admin"))

@main.route("/admin/dokumentasi")
@login_required
def admin_dokumentasi():
    activities = Activity.query.order_by(Activity.tanggal.desc()).all()

    return render_template(
        "admin/dokumentasi.html",
        activities=activities
    )

@main.route("/admin/dokumentasi/add", methods=["POST"])
@login_required
def add_activity():
    nama_kegiatan = request.form.get("nama_kegiatan", "").strip()
    tanggal = request.form.get("tanggal", "").strip()

    images = request.files.getlist("images")

    if not nama_kegiatan:
        flash("Nama kegiatan wajib diisi.", "danger")
        return redirect(url_for("main.admin_dokumentasi"))

    if not tanggal:
        flash("Tanggal kegiatan wajib diisi.", "danger")
        return redirect(url_for("main.admin_dokumentasi"))

    valid_images = [
        image for image in images
        if image and image.filename
    ]

    if not valid_images:
        flash("Minimal satu foto harus dipilih.", "danger")
        return redirect(url_for("main.admin_dokumentasi"))

    activity = Activity(
        nama_kegiatan=nama_kegiatan,
        tanggal=tanggal
    )

    db.session.add(activity)
    db.session.flush()

    upload_folder = os.path.join(
        current_app.static_folder,
        "uploads"
    )

    os.makedirs(upload_folder, exist_ok=True)

    for image in valid_images:
        filename = secure_filename(image.filename)

        if not filename:
            continue

        base, extension = os.path.splitext(filename)
        counter = 1
        final_filename = filename

        while os.path.exists(
            os.path.join(upload_folder, final_filename)
        ):
            final_filename = f"{base}_{counter}{extension}"
            counter += 1

        image.save(
            os.path.join(upload_folder, final_filename)
        )

        activity_image = ActivityImage(
            filename=final_filename,
            activity_id=activity.id
        )

        db.session.add(activity_image)

    db.session.commit()

    flash("Dokumentasi kegiatan berhasil ditambahkan.", "success")

    return redirect(url_for("main.admin_dokumentasi"))

@main.route(
    "/admin/activity/<int:activity_id>/delete",
    methods=["POST"]
)
@login_required
def delete_activity(activity_id):

    activity = Activity.query.get_or_404(
        activity_id
    )


    for image in activity.images:

        path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            image.filename
        )


        if os.path.exists(path):

            os.remove(path)


    db.session.delete(
        activity
    )

    db.session.commit()


    flash(
        "Dokumentasi kegiatan berhasil dihapus.",
        "success"
    )


    return redirect(
        url_for(
            "main.admin",
            _anchor="dokumentasi"
        )
    )

@main.route(
    "/admin/activity/image/<int:image_id>/delete",
    methods=["POST"]
)
@login_required
def delete_activity_image(image_id):

    image = ActivityImage.query.get_or_404(
        image_id
    )

    activity_id = image.activity_id

    path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        image.filename
    )

    if os.path.exists(path):

        os.remove(path)

    db.session.delete(
        image
    )

    db.session.commit()

    flash(
        "Foto berhasil dihapus.",
        "success"
    )

    return redirect(
        url_for(
            "main.admin",
            _anchor="dokumentasi"
        )
    )

@main.route("/admin/riwayat")
@login_required
def admin_riwayat():
    sync_current_year()
    
    history_chart = PopulationHistory.query.order_by(
        PopulationHistory.tahun.asc()
    ).all()

    history_years = [item.tahun for item in history_chart]
    history_counts = [item.jumlah for item in history_chart]

    history = PopulationHistory.query.order_by(
        PopulationHistory.tahun.desc()
    ).all()

    prediction = predict_next_year()

    return render_template(
        "admin/riwayat.html",

        history=history,
        history_years=history_years,
        history_counts=history_counts,
        prediction=prediction
    )

@main.route("/admin/riwayat/add", methods=["POST"])
@login_required
def add_history():
    tahun = request.form.get("tahun", "").strip()
    jumlah = request.form.get("jumlah", "").strip()

    if not tahun.isdigit():
        flash("Tahun harus berupa angka.", "danger")
        return redirect(url_for("main.admin_riwayat"))

    if not jumlah.isdigit():
        flash("Jumlah penduduk harus berupa angka.", "danger")
        return redirect(url_for("main.admin_riwayat"))

    tahun = int(tahun)
    jumlah = int(jumlah)

    if tahun < 1900 or tahun > 2100:
        flash("Tahun tidak valid.", "danger")
        return redirect(url_for("main.admin_riwayat"))

    if jumlah < 0:
        flash("Jumlah penduduk tidak boleh negatif.", "danger")
        return redirect(url_for("main.admin_riwayat"))

    existing = PopulationHistory.query.filter_by(
        tahun=tahun
    ).first()

    if existing:
        flash("Data untuk tahun tersebut sudah ada.", "danger")
        return redirect(url_for("main.admin_riwayat"))

    history = PopulationHistory(
        tahun=tahun,
        jumlah=jumlah
    )

    db.session.add(history)
    db.session.commit()

    flash("Data riwayat berhasil ditambahkan.", "success")

    return redirect(url_for("main.admin_riwayat"))

@main.route("/admin/backup")
@login_required
def backup():
    backup_folder = os.path.join(
        current_app.instance_path,
        "backups"
    )

    os.makedirs(backup_folder, exist_ok=True)

    files = []

    for filename in os.listdir(backup_folder):
        if filename.lower().endswith(".csv"):
            filepath = os.path.join(
                backup_folder,
                filename
            )

            files.append({
                "filename": filename,
                "created": datetime.fromtimestamp(
                    os.path.getmtime(filepath)
                )
            })

    files.sort(
        key=lambda item: item["created"],
        reverse=True
    )

    return render_template(
        "admin/backup.html",
        backup_files=files
    )
    
@main.route("/admin/backup/create", methods=["POST"])
@login_required
def create_backup():

    backup_folder = os.path.join(
        current_app.instance_path,
        "backups"
    )

    os.makedirs(
        backup_folder,
        exist_ok=True
    )

    now = datetime.now()

    filename = (
        f"backup_penduduk_"
        f"{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    )

    filepath = os.path.join(
        backup_folder,
        filename
    )

    residents = Resident.query.order_by(
        Resident.nama.asc()
    ).all()

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "tanggal_backup",
            "nik",
            "nama",
            "jenis_kelamin",
            "dusun",
            "tanggal_lahir",
            "pekerjaan",
            "pendidikan"
        ])

        tanggal_backup = now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        for resident in residents:

            writer.writerow([
                tanggal_backup,
                resident.nik,
                resident.nama,
                resident.jenis_kelamin,
                resident.dusun,
                resident.tanggal_lahir,
                resident.pekerjaan,
                resident.pendidikan
            ])

    flash(
        f"Backup berhasil dibuat: {filename}",
        "success"
    )

    return redirect(
        url_for("main.backup")
    )

@main.route("/admin/backup/download/<filename>")
@login_required
def download_backup(filename):

    backup_folder = os.path.join(
        current_app.instance_path,
        "backups"
    )

    return send_from_directory(
        backup_folder,
        filename,
        as_attachment=True
    )
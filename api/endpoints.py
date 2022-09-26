from collections import Counter
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import text

from api.config import get_connection

kunjungan_bp = Blueprint("kunjungan", __name__)
engine = get_connection()


def get_default_date(tgl_awal, tgl_akhir):
    if tgl_awal == None:
        tgl_awal = datetime.today() - relativedelta(months=1)
        tgl_awal = tgl_awal.strftime('%Y-%m-%d')
    else:
        tgl_awal = datetime.strptime(tgl_awal, '%Y-%m-%d')

    if tgl_akhir == None:
        tgl_akhir = datetime.strptime(datetime.today().strftime('%Y-%m-%d'),
                                      '%Y-%m-%d')
    else:
        tgl_akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
    return tgl_awal, tgl_akhir


def get_categorical_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) <
                                          (birth_date.month, birth_date.day))
    category = '<5' if age<5 else '5-14' if age>=5 and age<15 else '15-24' if age>=15 and age<=24 \
            else '25-34' if age>=25 and age<=34 else '35-44' if age>=35 and age<=44 else '45-54' if age>=45 and age<=54 \
            else '55-64' if age>=55 and age<=64 else '>65'
    return category


def count_values(data, param):
    cnt = Counter()
    for i in range(len(data)):
        cnt[data[i][param].lower().replace(' ', '_')] += 1
    return cnt


@kunjungan_bp.route('/card_pasien')
def card_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, i.NamaInstalasi
            FROM rsudtasikmalaya.dbo.PasienDaftar pd
            INNER JOIN rsudtasikmalaya.dbo.Ruangan r
            ON pd.KdRuanganAkhir  = r.KdRuangan  
            INNER JOIN rsudtasikmalaya.dbo.Instalasi i
            ON r.KdInstalasi = i.KdInstalasi
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "instalasi": row['NamaInstalasi'].split("\r")[0]
        })
    result = {
        "judul": 'Instalasi (Card Kunjungan)',
        "label": 'Kunjungan Pasien',
        "instalasi": count_values(data, 'instalasi'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


# Detail Card kunjungan (pop up table)
@kunjungan_bp.route('/detail_card_pasien')
def detail_card_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pd.TglPendaftaran, pd.NoPendaftaran, pd.NoCM, p.Title, p.NamaLengkap, p.TglLahir, p.JenisKelamin, p.Alamat
            FROM rsudtasikmalaya.dbo.PasienDaftar pd
            INNER JOIN rsudtasikmalaya.dbo.Pasien p
            ON pd.NoCM  = p.NoCM
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "no_daftar": row['NoPendaftaran'],
            "no_cm": row['NoCM'],
            "nama": row['Title'] + ' ' + row['NamaLengkap'],
            "tgl_lahir": row['TglLahir'],
            "jenis_kelamin": row['JenisKelamin'],
            "alamat": row['Alamat'],
            "judul": "Detail (Card Kunjungan)",
            "label": "Kunjungan Pasien"
        })
    return jsonify(data)


@kunjungan_bp.route('/kelas_perawatan')
def kelas_perawatan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, kp.DeskKelas as NamaKelas
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.KelasPelayanan kp
            ON pd.KdKelasAkhir = kp.KdKelas
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "kelas": row['NamaKelas']
        })
    result = {
        "judul": "Kelas Perawatan",
        "label": "Kunjungan Pasien",
        "kelas": count_values(data, 'kelas'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/kelompok_pasien')
def kelompok_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, kp.JenisPasien as KelompokPasien
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.KelompokPasien kp
            ON pd.KdKelasAkhir = kp.KdKelompokPasien
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "kelompok": row['KelompokPasien']
        })
    result = {
        "judul": 'Kelompok Pasien',
        "label": 'Kunjungan Pasien',
        "kelompok": count_values(data, 'kelompok'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/rujukan')
def rujukan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, ra.RujukanAsal
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.Rujukan r
            ON pd.NoCM = r.NoCM
            INNER JOIN dbo.RujukanAsal ra
            ON r.KdRujukanAsal = ra.KdRujukanAsal
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "rujukan": row['RujukanAsal']
        })
    result = {
        "judul": 'Rujukan Asal Pasien',
        "label": 'Kunjungan Pasien',
        "rujukan": count_values(data, 'rujukan'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/status_pulang')
def status_pulang():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(f"""SELECT pp.TglPulang, sp.StatusPulang
            FROM dbo.StatusPulang sp
            INNER JOIN dbo.PasienPulang pp
            ON sp.KdStatusPulang = pp.KdStatusPulang
            WHERE pp.TglPulang >= '{tgl_awal}'
            AND pp.TglPulang < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pp.TglPulang ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPulang'],
            "status": row['StatusPulang']
        })
    result = {
        "judul": 'Status Pulang',
        "label": 'Kunjungan Pasien',
        "status": count_values(data, 'status'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/umur_jenis_kelamin')
def umur_jenis_kelamin():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, p.TglLahir, p.JenisKelamin
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.Pasien p
            ON pd.NoCM = p.NoCM 
            WHERE pd.TglPendaftaran >= '{tgl_awal}' 
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "umur": get_categorical_age(row['TglLahir']),
            "jenis_kelamin": row['JenisKelamin']
        })
    result = {
        "judul": 'Umur dan Jenis Kelamin',
        "label": 'Kunjungan Pasien',
        "jenis_kelamin": count_values(data, 'jenis_kelamin'),
        "umur": count_values(data, 'umur'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/pendidikan')
def pendidikan():
    return jsonify({"response": "ini data pendidikan"})


@kunjungan_bp.route('/pekerjaan')
def pekerjaan():
    return jsonify({"response": "ini data pekerjaan"})

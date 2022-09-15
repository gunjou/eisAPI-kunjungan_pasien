from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import text

from api.config import get_connection


kunjungan_bp = Blueprint("kunjungan", __name__)
engine = get_connection()


def get_default_date(tgl_awal, tgl_akhir):
    if tgl_awal == None:
        tgl_awal = datetime.today().strftime('%Y-%m-%d')
    else:
        tgl_awal = datetime.strptime(tgl_awal, '%Y-%m-%d')
    if tgl_akhir == None:
        tgl_akhir = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
    return tgl_awal, tgl_akhir


@kunjungan_bp.route('/card_pasien')
def card_pasien():
    return jsonify({"response": "ini data card_pasien"})


@kunjungan_bp.route('/kelas_perawatan', methods=['GET'])
def kelas_perawatan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pd.TglPendaftaran, kp.DeskKelas as NamaKelas
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
            "kelas": row['NamaKelas'],
            "judul": "Kelas Perawatan",
            "label": "Kunjungan Pasien"
            })
    return jsonify(data)


@kunjungan_bp.route('/kelompok_pasien')
def kelompok_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pd.TglPendaftaran, kp.JenisPasien as KelompokPasien
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
            "kelompok": row['KelompokPasien'],
            "judul": 'Kelompok Pasien',
            "label": 'Kunjungan Pasien'
        })
    return jsonify(data)


@kunjungan_bp.route('/rujukan')
def rujukan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pd.TglPendaftaran, ra.RujukanAsal
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
            "rujukan": row['RujukanAsal'],
            "judul": 'Rujukan Asal Pasien',
            "label": 'Kunjungan Pasien'
        })
    return jsonify(data)


@kunjungan_bp.route('/status_pulang')
def status_pulang():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pp.TglPulang, sp.StatusPulang
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
            "status": row['StatusPulang'],
            "judul": 'Status Pulang',
            "label": 'Kunjungan Pasien'
        })
    return jsonify(data)


@kunjungan_bp.route('/umur_jenis_kelamin')
def umur_jenis_kelamin():
    return jsonify({"response": "ini data umur_jenis_kelamin"})


@kunjungan_bp.route('/pendidikan')
def pendidikan():
    return jsonify({"response": "ini data pendidikan"})


@kunjungan_bp.route('/pekerjaan')
def pekerjaan():
    return jsonify({"response": "ini data pekerjaan"})

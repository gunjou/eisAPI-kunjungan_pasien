from collections import Counter
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request

from api.query import *

kunjungan_bp = Blueprint("kunjungan", __name__)


def get_default_date(tgl_awal, tgl_akhir):
    if tgl_awal == None:
        tgl_awal = datetime.strptime((datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_awal = datetime.strptime(tgl_awal, '%Y-%m-%d')

    if tgl_akhir == None:
        tgl_akhir = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
    return tgl_awal, tgl_akhir


def get_date_prev(tgl_awal, tgl_akhir):
    tgl_awal = tgl_awal - relativedelta(months=1)
    tgl_awal = tgl_awal.strftime('%Y-%m-%d')
    tgl_akhir = tgl_akhir - relativedelta(months=1)
    tgl_akhir = tgl_akhir.strftime('%Y-%m-%d')
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
        # cnt[data[i][param].lower().replace(' ', '_')] += 1
        cnt[data[i][param]] += 1
    return cnt


@kunjungan_bp.route('/kunjungan/card_pasien')
def card_pasien():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_card_pasien(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_card_pasien(tgl_awal, tgl_akhir + timedelta(days=1))

    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPendaftaran'], "instalasi": row['NamaInstalasi'].split("\r")[0]} for row in result]
    tmp_prev = [{"tanggal": row['TglPendaftaran'], "instalasi": row['NamaInstalasi'].split("\r")[0]} for row in result_prev]   

    # Extract data as (dataframe)
    cnts = count_values(tmp, 'instalasi')
    cnts_prev = count_values(tmp_prev, 'instalasi')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None
    
    # Define return result as a json
    result = {
        "judul": "Instalasi (Card Kunjungan)",
        "label": "Kunjungan Pasien",
        "data": data, #count_values(tmp, 'instalasi'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


# Detail Card kunjungan (pop up table)
@kunjungan_bp.route('/kunjungan/detail_card_pasien')
def detail_card_pasien():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    # Get query result
    result = query_detail_card_pasien(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Define return result as a json
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


@kunjungan_bp.route('/kunjungan/kelas_perawatan')
def kelas_perawatan():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_kelas_perawatan(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_kelas_perawatan(tgl_awal, tgl_akhir + timedelta(days=1))

    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPendaftaran'], "kelas": row['NamaKelas']} for row in result]
    tmp_prev = [{"tanggal": row['TglPendaftaran'], "kelas": row['NamaKelas']} for row in result_prev]
    
    # Extract data as (dataframe)
    cnts = count_values(tmp, 'kelas')
    cnts_prev = count_values(tmp_prev, 'kelas')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None
    
    # Define return result as a json
    result = {
        "judul": "Kelas Perawatan",
        "label": "Kunjungan Pasien",
        "data": data, #count_values(tmp, 'kelas'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/kunjungan/kelompok_pasien')
def kelompok_pasien():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_kelompok_pasien(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_kelompok_pasien(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPendaftaran'], "kelompok": row['KelompokPasien']} for row in result]
    tmp_prev = [{"tanggal": row['TglPendaftaran'], "kelompok": row['KelompokPasien']} for row in result_prev]
    
    # Extract data as (dataframe)
    cnts = count_values(tmp, 'kelompok')
    cnts_prev = count_values(tmp_prev, 'kelompok')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None

    # Define return result as a json
    result = {
        "judul": 'Kelompok Pasien',
        "label": 'Kunjungan Pasien',
        "data": data, #count_values(tmp, 'kelas'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/kunjungan/rujukan')
def rujukan():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_rujukan(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_rujukan(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPendaftaran'], "rujukan": row['RujukanAsal']} for row in result]
    tmp_prev = [{"tanggal": row['TglPendaftaran'], "rujukan": row['RujukanAsal']} for row in result_prev]
    
    # Extract data as (dataframe)
    cnts = count_values(tmp, 'rujukan')
    cnts_prev = count_values(tmp_prev, 'rujukan')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None

    # Define return result as a json
    result = {
        "judul": 'Rujukan Asal Pasien',
        "label": 'Kunjungan Pasien',
        "data": data, #count_values(data, 'rujukan'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/kunjungan/status_pulang')
def status_pulang():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_status_pulang(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_status_pulang(tgl_awal, tgl_akhir + timedelta(days=1))
  
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPulang'], "status": row['StatusPulang']} for row in result]
    tmp_prev = [{"tanggal": row['TglPulang'], "status": row['StatusPulang']} for row in result_prev]
        
    # Extract data as (dataframe)
    cnts = count_values(tmp, 'status')
    cnts_prev = count_values(tmp_prev, 'status')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None

    # Define return result as a json
    result = {
        "judul": 'Status Pulang',
        "label": 'Kunjungan Pasien',
        "data": data, #count_values(data, 'status'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/kunjungan/umur_jenis_kelamin')
def umur_jenis_kelamin():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_umur_jenis_kelamin(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_umur_jenis_kelamin(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPendaftaran'], "umur": get_categorical_age(row['TglLahir']), "jenis_kelamin": row['JenisKelamin']} for row in result]
    tmp_prev = [{"tanggal": row['TglPendaftaran'], "umur": get_categorical_age(row['TglLahir']), "jenis_kelamin": row['JenisKelamin']} for row in result_prev]
  
    # Extract data as (dataframe)
    cnts = count_values(tmp, 'umur')
    data, data_prev = [], []
    kategori_umur = [x for x, y in cnts.items()]
    for i in kategori_umur:
        p = 0
        l = 0
        for j in range(len(tmp)):
            if tmp[j]['umur'] == i and tmp[j]['jenis_kelamin'] == 'P':
                p += 1
            elif tmp[j]['umur'] == i and tmp[j]['jenis_kelamin'] == 'L':
                l += 1
            else:
                pass
        data.append({"name": i, "value": l+p, "laki_laki": l, "perempuan": p})

    for i in kategori_umur:
        p = 0
        l = 0
        for j in range(len(tmp_prev)):
            if tmp_prev[j]['umur'] == i and tmp_prev[j]['jenis_kelamin'] == 'P':
                p += 1
            elif tmp_prev[j]['umur'] == i and tmp_prev[j]['jenis_kelamin'] == 'L':
                l += 1
            else:
                pass
        data_prev.append({"name": i, "value": l+p, "laki_laki": l, "perempuan": p})
    
    # Define trend percentage
    for i in range(len(data)):
        percentage = None
        for j in range(len(data_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None

    # Define return result as a json
    result = {
        "judul": 'Umur dan Jenis Kelamin',
        "label": 'Kunjungan Pasien',
        "data": data,
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@kunjungan_bp.route('/kunjungan/pendidikan')
def pendidikan():
    return jsonify({"response": "ini data pendidikan"})


@kunjungan_bp.route('/kunjungan/pekerjaan')
def pekerjaan():
    return jsonify({"response": "ini data pekerjaan"})

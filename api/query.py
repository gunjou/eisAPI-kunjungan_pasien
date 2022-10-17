from sqlalchemy import text

from api.config import get_connection

engine = get_connection()


def query_card_pasien(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, i.NamaInstalasi
            FROM rsudtasikmalaya.dbo.PasienDaftar pd
            INNER JOIN rsudtasikmalaya.dbo.Ruangan r
            ON pd.KdRuanganAkhir  = r.KdRuangan  
            INNER JOIN rsudtasikmalaya.dbo.Instalasi i
            ON r.KdInstalasi = i.KdInstalasi
            WHERE pd.TglPendaftaran >= '{start_date}'
            AND pd.TglPendaftaran < '{end_date}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    return result


def query_detail_card_pasien(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, pd.NoPendaftaran, pd.NoCM, p.Title, p.NamaLengkap, p.TglLahir, p.JenisKelamin, p.Alamat
            FROM rsudtasikmalaya.dbo.PasienDaftar pd
            INNER JOIN rsudtasikmalaya.dbo.Pasien p
            ON pd.NoCM  = p.NoCM
            WHERE pd.TglPendaftaran >= '{start_date}'
            AND pd.TglPendaftaran < '{end_date}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    return result


def query_kelas_perawatan(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, kp.DeskKelas as NamaKelas
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.KelasPelayanan kp
            ON pd.KdKelasAkhir = kp.KdKelas
            WHERE pd.TglPendaftaran >= '{start_date}'
            AND pd.TglPendaftaran < '{end_date}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    return result


def query_kelompok_pasien(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, kp.JenisPasien as KelompokPasien
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.KelompokPasien kp
            ON pd.KdKelasAkhir = kp.KdKelompokPasien
            WHERE pd.TglPendaftaran >= '{start_date}'
            AND pd.TglPendaftaran < '{end_date}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    return result


def query_rujukan(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, ra.RujukanAsal
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.Rujukan r
            ON pd.NoCM = r.NoCM
            INNER JOIN dbo.RujukanAsal ra
            ON r.KdRujukanAsal = ra.KdRujukanAsal
            WHERE pd.TglPendaftaran >= '{start_date}'
            AND pd.TglPendaftaran < '{end_date}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    return result


def query_status_pulang(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pp.TglPulang, sp.StatusPulang
            FROM dbo.StatusPulang sp
            INNER JOIN dbo.PasienPulang pp
            ON sp.KdStatusPulang = pp.KdStatusPulang
            WHERE pp.TglPulang >= '{start_date}'
            AND pp.TglPulang < '{end_date}'
            ORDER BY pp.TglPulang ASC;"""))
    return result


def query_umur_jenis_kelamin(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT pd.TglPendaftaran, p.TglLahir, p.JenisKelamin
            FROM dbo.PasienDaftar pd
            INNER JOIN dbo.Pasien p
            ON pd.NoCM = p.NoCM 
            WHERE pd.TglPendaftaran >= '{start_date}'
            AND pd.TglPendaftaran < '{end_date}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    return result

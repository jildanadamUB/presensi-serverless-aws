import json
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SesiKuliah')
sns = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:846709910961:NotifikasiPresensi'


def now_wib():
    return datetime.now(
        ZoneInfo("Asia/Jakarta")
    )


def response(status, message):
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': message
        })
    }


def lambda_handler(event, context):

    try:

        body = json.loads(event['body']) if 'body' in event else event

        aksi = body.get('aksi', 'mulai')
        id_matakuliah = body.get('id_matakuliah')

        if not id_matakuliah:
            return response(
                400,
                "Mata kuliah wajib dipilih!"
            )

        # =====================================================
        # BERSIHKAN SESI JADWAL YANG SUDAH LEWAT
        # =====================================================

        hasil_query = table.query(
            KeyConditionExpression=Key(
                'id_matakuliah'
            ).eq(id_matakuliah)
        )

        for item in hasil_query.get('Items', []):

            if item.get('status') != 'Aktif':
                continue

            if item.get('tipe_sesi') != 'jadwal':
                continue

            try:

                dt_selesai = datetime.strptime(
                    item['waktu_selesai'],
                    "%Y-%m-%d %H:%M:%S"
                )

                sekarang = now_wib().replace(
                    tzinfo=None
                )

                if sekarang > dt_selesai:

                    table.update_item(
                        Key={
                            'id_matakuliah':
                                item['id_matakuliah'],
                            'waktu':
                                item['waktu']
                        },
                        UpdateExpression=
                            "SET #st = :s",
                        ExpressionAttributeNames={
                            '#st': 'status'
                        },
                        ExpressionAttributeValues={
                            ':s': 'Selesai'
                        }
                    )

            except Exception as e:
                print(
                    "Auto-close error:",
                    str(e)
                )

        # =====================================================
        # AKHIRI SESI
        # =====================================================

        if aksi == 'akhiri':

            hasil_query = table.query(
                KeyConditionExpression=Key(
                    'id_matakuliah'
                ).eq(id_matakuliah)
            )

            sesi_aktif = None

            for item in hasil_query.get('Items', []):

                if item.get('status') == 'Aktif':
                    sesi_aktif = item
                    break

            if not sesi_aktif:

                return response(
                    404,
                    "Tidak ada sesi aktif."
                )

            waktu_selesai = now_wib().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            table.update_item(
                Key={
                    'id_matakuliah':
                        sesi_aktif['id_matakuliah'],
                    'waktu':
                        sesi_aktif['waktu']
                },
                UpdateExpression="""
                    SET #st = :s,
                        waktu_selesai = :ws
                """,
                ExpressionAttributeNames={
                    '#st': 'status'
                },
                ExpressionAttributeValues={
                    ':s': 'Selesai',
                    ':ws': waktu_selesai
                }
            )

            return response(
                200,
                "Sesi berhasil diakhiri!"
            )

        # =====================================================
        # BUAT SESI BARU
        # =====================================================

        topik = body.get('topik')
        tipe_sesi = body.get('tipe_sesi')

        if not topik:

            return response(
                400,
                "Topik wajib diisi!"
            )

        hasil_query = table.query(
            KeyConditionExpression=Key(
                'id_matakuliah'
            ).eq(id_matakuliah)
        )

        for item in hasil_query.get('Items', []):

            if item.get('status') == 'Aktif':

                return response(
                    400,
                    "Masih ada sesi aktif yang belum ditutup!"
                )

        # =====================================================
        # SESI REALTIME
        # =====================================================

        if tipe_sesi == 'langsung':

            waktu_mulai = now_wib().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            item = {
                'id_matakuliah': id_matakuliah,
                'waktu': waktu_mulai,
                'waktu_selesai': '-',
                'topik': topik,
                'status': 'Aktif',
                'tipe_sesi': 'langsung'
            }

        # =====================================================
        # SESI TERJADWAL
        # =====================================================

        else:

            tanggal = body.get('tanggal')
            jam_mulai = body.get('waktu_mulai')
            jam_selesai = body.get('waktu_selesai')

            if not tanggal \
               or not jam_mulai \
               or not jam_selesai:

                return response(
                    400,
                    "Tanggal dan jam wajib diisi!"
                )

            waktu_mulai = f"{tanggal} {jam_mulai}:00"

            waktu_selesai = f"{tanggal} {jam_selesai}:00"

            item = {
                'id_matakuliah': id_matakuliah,
                'waktu': waktu_mulai,
                'waktu_selesai': waktu_selesai,
                'topik': topik,
                'status': 'Aktif',
                'tipe_sesi': 'jadwal'
            }

        table.put_item(
            Item=item
        )

        # =====================================================
        # SNS EMAIL
        # =====================================================

        try:

            pesan = f"""
Halo Mahasiswa,

Sesi presensi baru telah dibuka.

Mata Kuliah : {id_matakuliah}
Topik       : {topik}
Waktu Mulai : {item['waktu']}
Waktu Akhir : {item['waktu_selesai']}

Silakan login ke dashboard mahasiswa.
"""

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"Presensi Dimulai: {id_matakuliah}",
                Message=pesan
            )

        except Exception as e:
            print(
                "SNS Error:",
                str(e)
            )

        return response(
            200,
            "Sesi berhasil dibuat & email terkirim!"
        )

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return response(
            500,
            str(e)
        )
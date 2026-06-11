import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SesiKuliah')

def lambda_handler(event, context):
    try:
        # Cari semua sesi yang berstatus Aktif
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('status').eq('Aktif')
        )
        items = response.get('Items', [])

        for sesi in items:
            waktu_selesai = sesi.get('waktu_selesai')

            # PERBAIKAN 1: Jika sesi Realtime, LANGSUNG TAMPILKAN ke mahasiswa (bukan di-skip)
            if waktu_selesai == 'Sesi Realtime (Aktif)' or waktu_selesai == '-':
                return {
                    'statusCode': 200,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'active': True,
                        'id_matakuliah': sesi.get('id_matakuliah'),
                        'topik': sesi.get('topik'),
                        'waktu': sesi.get('waktu'),
                        'waktu_selesai': sesi.get('waktu_selesai')
                    })
                }

            # PERBAIKAN 2: Jika sesi Terjadwal, cek apakah waktunya sudah habis
            try:
                # Format waktu disamakan dengan FungsiBukaKelas (YYYY-MM-DD HH:MM:SS)
                dt_selesai = datetime.strptime(waktu_selesai, "%Y-%m-%d %H:%M:%S")

                if datetime.now() > dt_selesai:
                    # Jika waktu sudah terlewat, tutup statusnya jadi Selesai
                    table.update_item(
                        Key={
                            'id_matakuliah': sesi['id_matakuliah'],
                            'waktu': sesi['waktu']
                        },
                        UpdateExpression="SET #st = :s",
                        ExpressionAttributeNames={'#st': 'status'},
                        ExpressionAttributeValues={':s': 'Selesai'}
                    )
                else:
                    # Jika masih dalam jadwal, tampilkan ke mahasiswa
                    return {
                        'statusCode': 200,
                        'headers': {'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({
                            'active': True,
                            'id_matakuliah': sesi.get('id_matakuliah'),
                            'topik': sesi.get('topik'),
                            'waktu': sesi.get('waktu'),
                            'waktu_selesai': sesi.get('waktu_selesai')
                        })
                    }

            except Exception as e:
                print("Format waktu tidak valid:", str(e))
                # Jika ada salah format dari database lama, tetap tampilkan agar tidak error
                return {
                    'statusCode': 200,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'active': True,
                        'id_matakuliah': sesi.get('id_matakuliah'),
                        'topik': sesi.get('topik')
                    })
                }

        # Jika looping selesai dan tidak ada yang aktif
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'active': False,
                'message': 'Tidak ada sesi presensi sekarang'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SesiKuliah')

def lambda_handler(event, context):

    try:

        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('status').eq('Aktif')
        )

        items = response.get('Items', [])

        for sesi in items:

            waktu_selesai = sesi.get('waktu_selesai')

            # Skip sesi realtime
            if waktu_selesai == 'Sesi Realtime (Aktif)' or waktu_selesai == '-':
                continue

            try:

                # Sesuaikan format dengan yang Anda simpan
                dt_selesai = datetime.strptime(
                    waktu_selesai,
                    "%Y-%m-%d %H:%M"
                )

                # Jika jadwal sudah lewat
                if datetime.now() > dt_selesai:

                    table.update_item(
                        Key={
                            'id_matakuliah': sesi['id_matakuliah'],
                            'waktu': sesi['waktu']
                        },
                        UpdateExpression="SET #st = :s",
                        ExpressionAttributeNames={
                            '#st': 'status'
                        },
                        ExpressionAttributeValues={
                            ':s': 'Selesai'
                        }
                    )

                else:

                    # Masih aktif, kirim ke frontend
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
            'body': json.dumps({
                'error': str(e)
            })
        }
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_presensi = dynamodb.Table('Presensi')
table_users = dynamodb.Table('Users')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if 'body' in event else event
        id_matakuliah = body.get('id_matakuliah')
        email = body.get('email')
        keterangan_presensi = body.get('keterangan_presensi')
        topik = body.get('topik') 
        
        if not id_matakuliah or not email or not keterangan_presensi or not topik:
            return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': 'Data presensi tidak lengkap!'})}
        
        # Cek apakah mahasiswa sudah absen di topik yang sama (Mencegah Absen Ganda)
        cek_absen = table_presensi.get_item(Key={'id_matakuliah': id_matakuliah, 'email': email})
        if 'Item' in cek_absen:
            item_lama = cek_absen['Item']
            if item_lama.get('topik') == topik:
                return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': 'Gagal: Anda sudah melakukan presensi untuk topik ini!'})}
        
        # Mengambil nama asli mahasiswa dari tabel Users
        user_res = table_users.get_item(Key={'email': email})
        nama_mhs = user_res.get('Item', {}).get('nama', 'Mahasiswa Tanpa Nama')
        
        table_presensi.put_item(
            Item={
                'id_matakuliah': id_matakuliah,
                'email': email,
                'nama': nama_mhs, 
                'topik': topik,  
                'keterangan_presensi': keterangan_presensi
            }
        )
        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': 'Notifikasi: Selesai presensi!'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': str(e)})}
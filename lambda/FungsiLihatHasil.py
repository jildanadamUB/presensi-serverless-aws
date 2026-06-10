import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_presensi = dynamodb.Table('Presensi')
table_users = dynamodb.Table('Users')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if 'body' in event else event
        id_matakuliah = body.get('id_matakuliah')
        topik = body.get('topik')
        
        if not id_matakuliah or not topik:
            return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': 'Mata kuliah dan Topik harus ditentukan!'})}
        
        # 1. Ambil daftar seluruh mahasiswa yang terdaftar di sistem
        users_response = table_users.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('role').eq('mahasiswa')
        )
        semua_mahasiswa = users_response.get('Items', [])
        
        # 2. Ambil semua data presensi untuk mata kuliah terkait
        presensi_response = table_presensi.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('id_matakuliah').eq(id_matakuliah)
        )
        data_presensi = presensi_response.get('Items', [])
        
        # Petakan mahasiswa yang sudah submit presensi pada topik spesifik ini
        peta_hadir = {}
        for p in data_presensi:
            if p.get('topik') == topik:
                peta_hadir[p['email']] = p.get('keterangan_presensi')
        
        # 3. Sinkronisasikan: jika belum ada data kirim, tandai otomatis sebagai "Tidak Hadir"
        hasil_rekap = []
        for mhs in semua_mahasiswa:
            email_mhs = mhs['email']
            nama_mhs = mhs.get('nama', 'Mahasiswa')
            
            status = peta_hadir.get(email_mhs, 'Tidak Hadir') 
            
            hasil_rekap.append({
                'nama': nama_mhs,
                'keterangan_presensi': status
            })
            
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'data': hasil_rekap})
        }
    except Exception as e:
        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'message': str(e)})}
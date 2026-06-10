import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if 'body' in event else event
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Email dan password wajib diisi!'})
            }
            
        response = table.get_item(Key={'email': email})
        
        if 'Item' in response:
            user = response['Item']
            if user.get('password') == password:
                return {
                    'statusCode': 200,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'message': 'Login berhasil',
                        'role': user.get('role'),
                        'nama': user.get('nama', 'Pengguna') # Mengembalikan data nama
                    })
                }
            else:
                return {
                    'statusCode': 401,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': 'Password salah!'})
                }
        else:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'User tidak ditemukan!'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Terjadi kesalahan sistem', 'error': str(e)})
        }
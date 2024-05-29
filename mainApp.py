# ~/web/mainApps.py

from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import base64
import os

# 애플리케이션 인스턴스 생성 및 템플릿 폴더 설정
template_folder = os.path.join('front')
app = Flask(__name__, template_folder=template_folder)
app.secret_key = 'your_secret_key_here'  # 세션 암호화를 위한 시크릿 키 설정

ssl_cert = '/home/ctf/web/CA_files/server.crt'
ssl_key = '/home/ctf/web/CA_files/server.key'

# 홈 페이지 라우트
@app.route('/')
def home():
    # 세션에 'username'이라는 키가 있는지 확인하여 로그인 상태를 체크
    if 'username' in session:
        # 세션에 'username'이 있으면 홈 페이지를 보여줌
        return render_template('homepage/index.html')
    else:
        # 세션에 'username'이 없으면 로그인 페이지로 리다이렉트
        return redirect(url_for('login'))

# 로그인 페이지 라우트
@app.route('/login')
def login():
    return render_template('login/index.html')

# 저장할 폴더 경로 설정
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'upload')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL 설정
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ctf'
app.config['MYSQL_PASSWORD'] = 'asdf'
app.config['MYSQL_DB'] = 'CTK'
mysql = MySQL(app)

@app.route('/loginCheck', methods=['POST'])
def login_check():
    try:
        if request.method == 'POST':
            #data = request.get_json()
            with app.app_context():
                #username = request.form['username']
                email = request.form['email']
                password = request.form['password']

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                query = 'SELECT * FROM CTK_USER WHERE email = %s AND password = %s'
                cursor.execute(query, (email, password))

                result = cursor.fetchone()
                if  result:
                    user_class = result['class']
                    return jsonify({'class': user_class})
                    #return render_template('login/faceLogin.html')
                else:
                    flash('Invalid username or password')
                    return redirect(url_for('login'))

        else:
            flash('Error!')
            return redirect(url_for('login'))

        return render_template('login/index.html')

    except Exception as e:
        # 에러가 발생한 경우 False 반환
        return jsonify(success=False, error=str(e))


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # 요청에서 JSON 데이터 추출
        data = request.get_json()

        # 데이터에서 이미지 데이터 추출
        image_data = data['image']

        # base64로 인코딩된 이미지 디코딩
        image_data = image_data.split(",")[1]  # "data:image/png;base64," 제거
        image_bytes = base64.b64decode(image_data)

        # 저장할 파일 이름 설정 (여기서는 예시로 'uploaded_image.png')
        file_path = os.path.join(UPLOAD_FOLDER, 'uploaded_image.png')

        # 파일 저장
        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        # 저장이 완료되었으면 클라이언트에게 True 반환
        return jsonify(success=True)

    except Exception as e:
        # 에러가 발생한 경우 False 반환
        return jsonify(success=False, error=str(e))

if __name__ == '__main__':
    app.run(host='192.168.219.170', port=8000, ssl_context=(ssl_cert, ssl_key))
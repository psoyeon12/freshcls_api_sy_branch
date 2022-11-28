from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import numpy as np
import cv2
import db_connector

import ssl

app = Flask(__name__, template_folder='web')
CORS(app, support_credentials=True)

FLUTTER_WEB_APP = 'web'


@app.route('/web/')
def render_page_web():
    return render_template('index.html')


@app.route('/web/<path:name>')
def return_flutter_doc(name):

    datalist = str(name).split('/')
    DIR_NAME = FLUTTER_WEB_APP

    if len(datalist) > 1:
        for i in range(0, len(datalist) - 1):
            DIR_NAME += '/' + datalist[i]

    return send_from_directory(DIR_NAME, datalist[-1])


@app.route('/run', methods=['POST'])
def run():

    # 저장할 위치 <= 나중에는 랜덤으로 경로와 파일명 작성해서 이미지 저장하고 DB에 저장해야 함
    save_file_nm = './test.jpg'

    # 일반 Post로 전송했을 경우 데이터를 받는 코드(기존 클라이언트)
    data = request.data

    # 기본 POST가 아니어서 data가 빈 값이면 multipart로 처리
    if data == b'':
        # file이라는 이름으로 첨부된 파일이 있는지 확인
        if 'file' in request.files:
            # test라는 이름으로 추가된 데이터 있는지 확인
            str_data = request.form['test']
            print(str_data)
            
            # FileStorage 포맷으로 받아와 일단 로컬에 저장
            file = request.files['file']
            file.save('./test.jpg')

            # 저장된 파일을 다시 읽어옴
            filestr = cv2.cvtColor(cv2.imread(save_file_nm, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)[:, :, :3]
            data = filestr
    else:
        # POST 방식이면 저장하고 추론 진행
        data = np.frombuffer(data, dtype='float32')

        int_np_data = np.array(data, dtype='int').reshape((299, 299, 3))
        cv2.imwrite(save_file_nm, int_np_data)

    np_data = data.reshape((299, 299, 3))

    np_data_nm = np_data / 255.0
    frame = np_data_nm.reshape((1, 299, 299, 3))

    cls_list = ['true']

    return jsonify({'result': 'ok', 'cls_list': cls_list})


@app.route('/get_model', methods=['GET', 'POST'])
def get_model():
    # GET 파라메터 받아와서 dict로 변환
    param_dict = request.args.to_dict()

    # 기본 모델 조회 쿼리(조건 언제나 TRUE)
    query = "SELECT * FROM model WHERE 1=1 "

    # 파라메터에 act_yn이 있으면 조건 추가
    cond = ''
    if 'act_yn' in param_dict:
        cond = f"AND act_yn = '{param_dict['act_yn']}'"
    query += cond

    # DB 객체 생성
    dbConn = db_connector.DbConn()
    # 쿼리 실행
    result = dbConn.select(query)

    # 결과 반환
    return jsonify({'result': 'ok', 'value': result})


def selectAsDict(self, query):
    try:
        self.cursor.execute(query)
        columns = list(self.cursor.description)
        result = self.cursor.fetchall()
        results = []

        for row in result:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col.name] = row[i]
            results.append(row_dict)
    except Exception as e:
        result = (" select DB err", e)

    return results

def on_json_loading_failed_return_dict(e):
    return {}



@app.route('/login', methods=['POST'])
def login():

    request.on_json_loading_failed = on_json_loading_failed_return_dict
    # DB에서 api 형태로 query 정보를 받아오는 코드

    query = "SELECT * FROM auth WHERE 1=1 "
    dbConn = db_connector.DbConn()
    login_data = dbConn.select(query=query)
    login_lst = []

    for data in login_data:
        login_dict = dict(zip(['id', 'password', 'login_no', 'act_yn'],data))
        login_lst.append(login_dict)

    # Flutter에서 해당 url로 email과 password를 post한 내용을 받아오는 코드

        # request 방식 확인 코드
    print(request.is_json)
    params = request.get_json()



    # Flutter에서 받아온 정보를 DB에서 받아온 정보와 비교하여 POST할 dict를 작성하는 코드

    # for dicta in login_lst:
    #     if dicta['id'] == param_dict['id']:
    #         dicta['act_yn'] = 'Y'
    #         dicta['auth_result'] = 'ok'
    #     elif dicta['password'] == param_dict['password']:
    #
    #     else:
    #         dicta['auth_yn'] = 'N'
    #         dicta['auth_result'] = 'fail'
    #
    # if len(auth_lst) > 0:
    #     auth_result = 'ok'
    # else:
    #     auth_result = 'fail'

    # 비교 후 작성된 dict 내용을 json 혹은 ajax 형태로 flutter에 전송하기 위한 코드

    return jsonify({'result': params})
    # return jsonify({'result': auth_lst, 'authorization_result' : auth_result})

@app.route('/log', methods=['GET', 'POST'])
def log():
    param_dict = request.args.to_dict()
    print(param_dict['test'])
    return jsonify({'result': 'ok'})


if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key', password='1234')
    app.run(host='0.0.0.0', port=9890, ssl_context=ssl_context, debug=True)


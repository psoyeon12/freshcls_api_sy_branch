@app.route('/login', methods=('GET', 'POST'))
def login():
    param_dict = request.form.get('body')

    print(param_dict)

    query = "SELECT * FROM auth WHERE 1=1 "

    cond = ''
    if 'act_yn' in param_dict:
        cond = f"AND act_yn = '{param_dict['act_yn']}'"
    query += cond

    if 'auth_cd' in param_dict:
        cond = f"AND auth_cd = '{param_dict['auth_cd']}'"
    query += cond

    dbConn = db_connector.DbConn()

    auth_data = dbConn.select(query=query)

    auth_lst = []

    for data in auth_data:
        auth_dict = dict(zip(['auth_cd', 'act_yn', 'auth_no'], data))
        auth_lst.append(auth_dict)

    for dicta in auth_lst:
        if dicta['auth_cd'] == param_dict['auth_cd']:
            dicta['act_yn'] = 'Y'
            dicta['auth_result'] = 'ok'
        else:
            dicta['auth_yn'] = 'N'
            dicta['auth_result'] = 'fail'

    if len(auth_lst) > 0:
        auth_result = 'ok'
    else:
        auth_result = 'fail'
    return jsonify({'result': param_dict})
    # return jsonify({'result': auth_lst, 'authorization_result' : auth_result})
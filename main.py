import streamlit as st
import sqlite3, requests, json

def connectDB(params):
    #host="http://127.0.0.1:9000/%s"%params['address']
    host="http://jbc0708.pythonanywhere.com/%s" % params['address']
    res = requests.post(host, data=json.dumps(params))
    return res.json()

if "year" not in st.session_state:
    st.session_state.year = 2017
    st.session_state.count = 1
    st.session_state.subject = 0
    st.session_state.start = 1
    st.session_state.number = 1
    st.session_state.type = '암기'
    st.session_state.keyword = ""

    st.session_state.before = -1
    st.session_state.current = 0
    st.session_state.data = []

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "메뉴를 선택하세요",
    ("문제타입 입력", "문제타입 확인", "데이터 초기화")
)

if add_selectbox == "문제타입 입력":
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
    with col1:
        years = range(2017, 2024)
        index_year = years.index(st.session_state.year)
        year = st.selectbox("기출년도", years, index=index_year)
    with col2:
        counts = (1, 2, 3)
        index_count = counts.index(st.session_state.count)
        count = st.selectbox("기출회차", counts,  index=index_count)
    with col3:
        subjects = ['전기자기학', '전력공학', '전기기기', '회로이론 및 제어공학', '전기설비기술기준']
        subject = st.selectbox("과목", subjects, index=st.session_state.subject)

    with col4:
        current = st.session_state.number + 1
        number = st.number_input("문제번호", 1, 100, current)
    
    qtype = st.selectbox("문제 유형", ("암기", "계산"), index=0)
    
    keyword = st.text_input("키워드 ex) 전기기기/와류손/히스테리시손", value="")

    submit = st.button("등록하기")

    if submit:
        if keyword != "": 
            if year: st.session_state.year = year
            if count: st.session_state.count = count
            if subject: 
                index_sub = subjects.index(subject)
                st.session_state.subject = index_sub
            if number: 
                st.session_state.number = number
            if qtype: st.session_state.type = qtype

            st.session_state.keyword = keyword

            params = {
                'address': 'checkNumber',
                'year': year,
                'count': count,
                'subject': index_sub,
                'number': number,
                'type': qtype,
                'keyword': keyword
            }
            result = connectDB(params)
            if result['error_state']: st.error(result['error_msg'])
            else: st.success("업데이트 완료")
        else: st.error("키워드를 입력하세요")

elif add_selectbox == '문제타입 확인':
    subjects = ('전기자기학', '전력공학', '전기기기', '회로이론 및 제어공학', '전기설비기술기준')
    subject = st.selectbox("과목", subjects, index=None)
    if subject: 
        index_sub = subjects.index(subject)
        if index_sub != st.session_state.before:
            st.session_state.before = index_sub
            st.session_state.current = 0
            params = {
                "address": "checkType",
                "subject": index_sub
            }
            result = connectDB(params)


        #"select id, year, count, number, type, keyword

            temp = result['data']
            data = [ [i[0], i[1], i[2], i[3], i[4], i[5].split("/"), 0] for i in temp ]
            if len(data) > 0:
                for i in data:
                    ids = []
                    for j in i[-2]:
                        for k in data:
                            if i[0] != k[0]:
                                if j in k[-2] and k[0] not in ids: ids.append(k[0])
                    i[-1] = len(ids)
            st.session_state.data = data

        data = st.session_state.data
        current = st.session_state.current
        if len(data) > 1:
            select = st.slider('문제번호', 1, len(data), current+1)
            if select: 
                current = select - 1
                st.session_state.current = current
                
            col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
            with col1:
                btn_left = st.button("Left", use_container_width=True, type="primary")
                if btn_left:
                    if st.session_state.current > 0:
                        st.session_state.current -= 1
                        st.rerun()
            with col2:
                btn_right = st.button("Right", use_container_width=True, type='primary')
                if btn_right:
                    if st.session_state.current < len(data) - 1:
                        st.session_state.current += 1
                        st.rerun()
            with col3:
                btn_delete = st.button("Delete", use_container_width=True, type='primary')
                if btn_delete:
                    target = data[select-1]
                    id = target[0]
                    params = {
                        'address': 'deleteInfo',
                        'id': id
                    }
                    st.session_state.data.pop(select-1)
                    data = st.session_state.data
                    result = connectDB(params)
                    st.rerun()
            
            target = data[select-1]
            q_id = "%s년 %s회 %s번째" % (target[1], target[2], target[3])
            id = st.text_input("문제 번호", value=q_id, disabled=True)
            type = st.text_input("문제 유형", value=target[4], disabled=True)
            temp_key = ""
            for i in data[select-1][-2]: temp_key += "%s/"%i
            keyword = st.text_input("문제 키워드", value=temp_key, disabled=True)
            st.text_input("문제 출제횟수", value=str(data[select-1][-1]), disabled=True)

elif add_selectbox == '데이터 초기화':
    with st.form("문제타입 입력", clear_on_submit=True):
        email = st.text_input("이메일", value="")
        phone = st.text_input("연락처", value="")
        submit = st.form_submit_button("초기화")
        if submit:
            params = {
                'address': 'clearDB',
                'email': email,
                'phone': phone
            }
            result = connectDB(params)
            if result['result'] == "All Clear":
                st.success("초기화가 완료되었습니다.")
            else:
                st.error("잘못된 입력으로 초기화가 실패하였습니다.")

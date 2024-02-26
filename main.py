import streamlit as st
import sqlite3

def connectDB(query, iscommit):
    db = sqlite3.connect("data.db")
    cu = db.cursor()
    cu.execute(query)
    if iscommit:
        db.commit()
        db.close()
        return None
    else:
        data = cu.fetchall()
        db.close()
        return data

def checkID(arr, subjects, subject):
    try:
        id = arr[0]
        keyowrd = arr[1]
        _id = int(id)
        query = "select id from info"
        data = connectDB(query, False)
        if _id in [ i[0] for i in data ]: raise Exception("중복된 ID 입니다.")
        year = id[:4]
        cnt = id[4]
        num = id[5:]
        if id == "" or keyword == "": raise Exception("빈칸을 입력 바랍니다.")
        if int(cnt) - 1 != subjects.index(subject): raise Exception("과목코드와 숫자가 일치하지 않습니다.")
        end = int(cnt) * 20 + 1
        if int(num) not in range(end-21, end): raise Exception("문제번호가 범위 안에 있지 않습니다.")
        return (False, None)
    except ValueError:
        return (True, "잘못된 ID 형식입니다.")
    except Exception as e:
        return (True, str(e))

if "current" not in st.session_state:
    st.session_state.current = 1

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "메뉴를 선택하세요",
    ("문제타입 입력", "문제타입 확인")
)

match add_selectbox:
    case '문제타입 입력':
        with st.form("문제타입 입력", clear_on_submit=True):
            id = st.text_input("문제 번호 ex:2023599", value="",  max_chars=8)
            subjects = ('전기자기학', '전력공학', '전기기기', '회로이론 및 제어공학', '전기설비기술기준')
            subject = st.selectbox("과목", subjects, index=0)
            qtype = st.selectbox("문제 유형", ("암기", "계산"), index=0)
            keyword = st.text_input("키워드 ex: 전기기기/와류손/히스테리시손", value="")
            submit = st.form_submit_button("등록하기")
            if submit:
                resultid = checkID((id, keyword), subjects, subject)
                try:
                    if resultid[0]: raise Exception(resultid[1])
                    else:
                        query = "insert into info(id,type,subject,keyword) values(%s,'%s','%s','%s')" % (id, qtype, subject, keyword)
                        connectDB(query, True)
                        st.success("등록이 완료되었습니다.")
                except Exception as e:
                    st.error("%s"% str(e))
                    
    case '문제타입 확인':
        subjects = ('전기자기학', '전력공학', '전기기기', '회로이론 및 제어공학', '전기설비기술기준')
        subject = st.selectbox("과목", subjects)
        query = "select id, type, keyword from info where subject='%s'" % subject
        temp = connectDB(query, False)
        data = []
        data = [ [i[0], i[1], i[2].split("/"), 0] for i in temp ]
        keyarr = [ i[2] for i in data ]
        if len(data) > 0:
            for i in data:
                cnt = 0
                for j in i[2]:
                    for keyword in keyarr:
                        if j in keyword: cnt += 1
                i[-1] = cnt
            current = st.session_state.current
            select = st.slider('문제번호', 1, len(data), current)
            id = st.text_input("문제 ID", value=str(data[select-1][0]), disabled=True)
            type = st.text_input("문제 유형", value=str(data[select-1][1]), disabled=True)
            temp_key = ""
            for i in data[select-1][2]: temp_key += "%s/"%i
            keyword = st.text_input("문제 키워드", value=temp_key, disabled=True)
            st.text_input("문제 출제횟수", value=str(data[select-1][3]), disabled=True)

import streamlit as st
import sqlite3, requests, json

def connectDB(params):
    #host="http://127.0.0.1:9000/%s"%params['address']
    host="http://jbc0708.pythonanywhere.com/%s" % params['address']
    res = requests.post(host, data=json.dumps(params))
    return res.json()


if "data" not in st.session_state:
    st.session_state.menu_choice = None

    st.session_state.data = {}
    st.session_state.chapter = None
    st.session_state.title = None

    st.session_state.check_subject = None
    st.session_state.check_data = []
    st.session_state.check_current = 0

add_selectbox = st.sidebar.selectbox(
    "메뉴를 선택하세요",
    ("치트키 입력", "치트키 암기확인", '치트키 수정/삭제')
)

if add_selectbox == "치트키 입력":
    st.session_state.data = {}
    st.session_state.chapter = None
    st.session_state.title = None
    with st.form("치트키 입력", border=True, clear_on_submit=True):
        cols= st.columns([3, 3, 3])
        with cols[0]:
            subjects = ['전기자기학', '전력공학', '전기기기', '회로이론', '제어공학', '전기설비기술기준',]
            w_subject = st.selectbox("과목", subjects, index=None)
        
        w_chapter = st.text_input("치트키 Chapter")
        w_kind = st.selectbox("치트키 Kind", ('공식', '암기'), index=0)
        w_title = st.text_input("치트키 Title")
        w_official = st.text_area("치트키 Official")
        w_submit = st.form_submit_button("등록하기")

        if w_submit:
            if w_subject == None or w_chapter == "" or w_title == "" or w_official == "":
                st.error("빈칸을 입력하세요")
            else:
                params = {
                    'address': 'registQuest',
                    'subject': w_subject,
                    'chapter': w_chapter,
                    'kind': w_kind,
                    'title': w_title,
                    'official': w_official
                }
                result = connectDB(params)
                if result['error_state']: st.error(result['error_msg'])
                else: st.success("업데이트 완료")


elif add_selectbox == "치트키 암기확인":
    cols= st.columns([3, 3, 3])
    with cols[0]:
        subjects = ['전기자기학', '전력공학', '전기기기', '회로이론', '제어공학', '전기설비기술기준']
        w_subject = st.selectbox("과목", subjects, index=None)

        if w_subject and w_subject != st.session_state.check_subject:
            st.session_state.check_data = []
            st.session_state.check_subject = w_subject
            st.session_state.check_current = 0
            params = {
                    'address': 'questChapter',
                    'subject': w_subject
                }
            result = connectDB(params)
            data = result['data']
            for i in data: i += [False, False]

            st.session_state.check_data = data

    with cols[2]:
        btn_submit = st.button("제출하기")

    len_quest = len(st.session_state.check_data)
    if len_quest > 0:
        current = st.session_state.check_current + 1
        w_qnum = st.slider("문제번호", 1, len_quest, current)

        btn_cols = st.columns([3, 3, 3, 3])
        with btn_cols[0]:
            btn_before = st.button("Left", use_container_width=True)
            if btn_before:
                if st.session_state.check_current > 0: 
                    st.session_state.check_current -= 1
                    st.rerun()

        with btn_cols[1]:
            btn_after = st.button("Right", use_container_width=True)
            if btn_after:
                if st.session_state.check_current < len(st.session_state.check_data) - 1: 
                    st.session_state.check_current += 1
                    st.rerun()

        target = st.session_state.check_data[st.session_state.check_current]
        w_chapter = st.text_input("치트키 Chapter", value=target[1], disabled=True)
        w_kind = st.selectbox("치트키 Kind", ['공식', '암기'], index=0 if target[2] == '공식' else 1, disabled=True)
        percent = "(정답률: %2d%%)" % int(target[6] / target[5] * 100) if target[5] > 0 else ""
        w_title = st.text_input("치트키 Title %s" % percent, value=target[3], disabled=True)
        
        check_cols = st.columns([3, 3, 3, 3])
        
        check_total = "O" if target[-2] else "X"
        check_right = "O" if target[-1] else "X"
        st.write("정답 확인: %s, 암기 확인: %s" % (check_total, check_right))
        
        with check_cols[0]:
            btn_show = st.button("정답보기", use_container_width=True)
            if btn_show:
                target[-2] = True
                if target[2] == '공식': st.latex(target[4])
                else: st.text_area(target[4], disabled=True)

        with check_cols[1]:
            btn_check = st.button("암기확인", use_container_width=True)
            if btn_check:
                target[-1] = not target[-1]



    if btn_submit:
        if len(st.session_state.check_data) > 0:
            target = st.session_state.check_data
            state = False
            for i in target:
                if i[-2] == False:
                    state = True
                    break
            if state:
                st.error("확인하지 않은 문제가 있습니다.")
            else:
                params = {
                    'address': 'updateChapter', 
                    'data': st.session_state.check_data
                }
                connectDB(params)
                st.session_state.check_data = []

                st.success("결과를 업데이트 했습니다.")



else:
    cols= st.columns([3, 3, 3])
    with cols[0]:
        subjects = ['전기자기학', '전력공학', '전기기기', '회로이론', '제어공학', '전기설비기술기준',]
        w_subject = st.selectbox("과목", subjects, index=None)
        if w_subject:
            st.session_state.data = {}
            st.session_state.chapter = None
            st.session_state.title = None
    
            params = {
                    'address': 'checkChapter',
                    'subject': w_subject
                }
            result = connectDB(params)
            data = result['data']
            st.session_state.data = data
    with cols[1]:
        w_update = st.selectbox('수정/삭제', ['Update', 'Delete'], index=0)

    data = st.session_state.data
    temp_chapters = tuple(data.keys())
    if len(temp_chapters) > 0:
        st.session_state.chapter = None
        st.session_state.title = None
        w_chapter = st.selectbox('치트키 Chapter', temp_chapters, index=None)
        if w_chapter: 
            st.session_state.chapter = w_chapter

    
    if st.session_state.chapter:
        data = st.session_state.data
        chapter = st.session_state.chapter
        titles = tuple(data[chapter])
        st.session_state.title = None
        w_title = st.selectbox('치트키 Title', titles, index=None)
        if w_title:
            st.session_state.title = w_title
    
    if st.session_state.title:
        data = st.session_state.data
        chapter = st.session_state.chapter
        title = st.session_state.title

        target = data[chapter][title]
        
        kind = target['kind']
        id = target['id']
        official = target['official']

        w_kind = st.selectbox('치트키 Kind', ['공식', '암기'], index=0 if kind =='공식' else 1)
        w_official = st.text_area('치트키 Official', value=official)
        w_submit = st.button('적용하기')

        if w_submit:
            params = {
                'address': 'updateQuest',
                'type': 'update' if w_update == 'Update' else 'delete',
                'id': target['id'],
                'kind': w_kind,
                'title': title,
                'official': w_official
            }
            result = connectDB(params)
            msg = "업데이트" if w_update == 'Update' else '삭제'
            st.success("%s 성공" % msg )
                
        

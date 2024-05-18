import streamlit as st
import pyodbc
import sys

def start_connection():
    # Australian Server Connection
    adfadf
    conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                "Server=LAPTOP-EITSFNFO;"
                "Database=RamaKrishna;"
                "Trusted_Connection=yes;")
    # Create a cursor from the connection
    cursor = conn.cursor()afdadf
    return conn, cursoradfadad

def check_any_changes_made(rec, qtext, option1, option2, option3, option4, soln):
    w_change_found = ""
    if qtext != rec['questiontext']:                
        st.markdown(f"**Current Question Text:** {rec['questiontext']} <br/> **New Question Text :** {qtext}",  unsafe_allow_html=True)
        w_change_found = "X"
    if option1 != rec['option1']:                
        st.markdown(f"**Current option1:** {rec['option1']} <br/> **New option1:** {option1}",  unsafe_allow_html=True)
        w_change_found = "X"
    if option2 != rec['option2']:
        st.markdown(f"**Current option2:** {rec['option2']} <br/> **New option2:** {option2}",  unsafe_allow_html=True)
        w_change_found = "X"
    if option3 != rec['option3']:
        st.markdown(f"**Current option3:** {rec['option3']} <br/> **New option3:** {option3}",  unsafe_allow_html=True)
        w_change_found = "X"
    if option4 != rec['option4']:
        st.markdown(f"**Current option4:** {rec['option4']} <br/> **New option4:** {option4}",  unsafe_allow_html=True)
        w_change_found = "X"
    if soln != rec['soln_long']:
        st.markdown(f"**Current Solution Long:** {rec['soln_long']} <br/> **New Solution Long:** {soln}",  unsafe_allow_html=True)
        w_change_found = "X"

    return w_change_found

def update_changes(w_connection, moodle_id, qtext, option1, option2, option3, option4, soln):
    conn = w_connection[0]
    cursor = w_connection[1]
                 
    try:
        
        # cursor.execute(f"UPDATE MOODLE_QUESTIONS SET questiontext = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, soln = ?, soln_long = ?  WHERE moodle_id = ?", (qtext, option1, option2, option3, option4, soln, soln, moodle_id))
        # conn.commit()
        # cursor.execute(f"UPDATE SOURCE_QUESTION SET questiontext = ?, answer1 = ?, answer2 = ?, answer3 = ?, answer4 = ?, correctfeedback = ?, soln_long = ?  WHERE moodle_id = ?", (qtext, option1, option2, option3, option4, soln, soln, moodle_id))
        # conn.commit()
        
        st.success('Saved changes')
    except pyodbc.Error as e:
        st.error(f"An error occurred updating table MOODLE_QUESTIONS : {e}")
    
    

# Ask the user for the Moodle question number
st.header('Update Questions in MOODLE_QUESTIONS and SOURCE_QUESTION Tables')
moodle_qno = st.text_input('Enter the Moodle question number', key='moodleqno')

if moodle_qno:
    # Query the database for the question
    if moodle_qno[0].upper() not in ['B', 'P', 'C']: # Not a valid question type
        st.error('Invalid Moodle Question number. It should start with B, P or C')
        sys.exit(1)
    else:
        moodle_id_like = "IN" + moodle_qno[0].upper() + "%"
    if moodle_qno[1:].isdigit() == False: # Not a valid question number
        st.error('Invalid Moodle Question number. The number part should be numeric')
        sys.exit(1)
    else:
        moodle_qno = int(moodle_qno[1:])
    rows = []
    w_connection = start_connection()
    conn = w_connection[0]
    cursor = w_connection[1]
    cursor.execute(f"SELECT * FROM MOODLE_QUESTIONS WHERE moodle_id LIKE ? AND moodle_qno = ?", (moodle_id_like,moodle_qno,))
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
            rows.append(dict(zip(columns, row)))
    if len(rows) == 1:
        rec = rows[0]
    elif len(rows) > 1:
        st.error('Multiple questions found with that number')
        sys.exit(1)
    else:
        st.error('No question found with that number')
        sys.exit(1)

    if rec:
        moodle_id = rec['moodle_id']
        # Display the fields and allow the user to edit them
        if len(rec['questiontext']) > 100:
            qtext = st.text_area('Question Text', rec['questiontext'], height=200)
        else:
            qtext = st.text_input('Question Text', rec['questiontext'])
        if len(rec['option1']) > 100:
            option1 = st.text_area('Option 1', rec['option1'])
        else:            
            option1 = st.text_input('Option 1', rec['option1'])
        if len(rec['option2']) > 100:
            option2 = st.text_area('Option 2', rec['option2'])
        else:
            option2 = st.text_input('Option 2', rec['option2'])
        if len(rec['option3']) > 100:
            option3 = st.text_area('Option 3', rec['option3'])
        else:
            option3 = st.text_input('Option 3', rec['option3'])
        if len(rec['option4']) > 100:
            option4 = st.text_area('Option 4', rec['option4'])
        else:
            option4 = st.text_input('Option 4', rec['option4'])
        if len(rec['soln_long']) > 100:            
            soln = st.text_area('Solution Long', rec['soln_long'], height=200)
        else:
            soln = st.text_input('Solution Long', rec['soln_long'])       

        w_change_found = check_any_changes_made(rec, qtext, option1, option2, option3, option4, soln)
        # Save or cancel buttons
        if st.button('Save'):
            # Update the database          
            
            if w_change_found == "X":
                update_changes(w_connection, moodle_id, qtext, option1, option2, option3, option4, soln)
                
            else:
                st.info('No changes found')
        elif st.button('Cancel'):
            st.info('Cancelled changes')
            del st.session_state['moodleqno']
            st.session_state['moodleqno'] = ""
            # Reset all the values to original values. But this is not happening
            st.rerun()

    else:
        st.error('No question found with that number')

    conn.close()

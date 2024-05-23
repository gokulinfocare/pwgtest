# This program uses XML data and use streamlit to update the data and then generate a new XML file
# Have to change the path mentioned for saving updated XML file
import streamlit as st 
import xml.etree.ElementTree as ET
import sys
import pandas as pd
import base64
import os
from function_moodle_xml_create import create_moodle_xml

# Function to get data from XML file
def get_data_from_xml():

    xml_table = []              # List to store the data from XML file
    new_filename = "updated.xml"   # Default name for updated XML file
    
    st.set_page_config(page_title="Please upload XML file to display/edit the data", layout="wide")
    
    file_name = st.file_uploader("Choose the XML file you want to display/edit")
    if file_name is not None:
        new_filename = file_name.name[:-4] + "updated.xml"
        file_contents = file_name.read().decode("utf-8")
        root = ET.fromstring(file_contents)
        xml_table = []
        #Takes data from the XML file uploaded and stores it in a list of dictionaries
        for element in root.findall('.//question'):
            if element.attrib['type'] == 'multichoice':
                moodle_id = qtext = soln = option1 = option2 = option3 = option4 = answer = ''     
                moodle_id = element.find('.//name/text').text
                qtext = element.find('.//questiontext/text').text                
                if 'Question ID' in qtext:
                    w_question_id = qtext.split('<br>')[0]
                soln = element.find('.//correctfeedback/text').text
                w_count = 1
                w_incorrect_feedback = ""
                xml_feedback = ""
                for rec in element.findall('.//answer'):
                    if w_incorrect_feedback == "":
                        if rec.find('feedback/text') is not None:
                            xml_feedback = rec.find('feedback/text').text
                        if xml_feedback is not None:
                            w_incorrect_feedback = xml_feedback
                    if w_count == 1:
                        option1 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'A'
                    elif w_count == 2:
                        option2 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'B'
                    elif w_count == 3:
                        option3 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'C'
                    elif w_count == 4:
                        option4 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'D'
                    w_count += 1
                qtext = qtext.replace('<br>', '\n')
                option1 = option1.replace('<br>', '\n')
                option2 = option2.replace('<br>', '\n')
                option3 = option3.replace('<br>', '\n')
                option4 = option4.replace('<br>', '\n')
                soln = soln.replace('<br>', '\n')
                w_incorrect_feedback = w_incorrect_feedback.replace('<br>', '\n')
                struc = {
                    'moodle_id': moodle_id,
                    'questiontext': qtext,                    
                    'option1': option1,
                    'option2': option2,
                    'option3': option3,
                    'option4': option4,
                    'answer': answer,
                    'soln': soln,
                    'incorrect_feedback': w_incorrect_feedback,
                    'question_id': w_question_id
                }
                xml_table.append(struc)
        # Get the filename from the file_uploader widget
        filename = file_name.name
        
        # Get the file extension
        file_extension = filename.split(".")[-1]
        
        # Create the new filename with "_updated.xml" suffix
        new_filename = filename.replace(f".{file_extension}", "_updated.xml")
        
        # Check if the number of records is 50
        if len(xml_table) != 50:
            print("50 records not found in XML file")
            sys.exit()
        
    return xml_table , new_filename         # Return the data and new filename

# Function to display original data 
def display_data(data):
    st.write("### Original Data:")
    st.dataframe(data)

# Function to edit data
def edit_data(data):
    st.write("### Edit Data:")
    num_rows = len(data)

    # Get column names from the keys of the first dictionary in the list
    if num_rows > 0:
        column_names = list(data[0].keys())
    else:
        column_names = []

    # Create empty DataFrame with columns
    edited_data = pd.DataFrame(columns=column_names, index=range(num_rows))
    w_count = 0
    w_en_lang = ""
    if data[0]['questiontext'].isascii():
        w_en_lang = "X"
    for rec in data:
        #w_count += 1
        if 'question_id' in rec:            
            st.write(f":blue[{rec['question_id']}]")            
            #st.write(question_id)        
        for key in rec.keys():
            if key == 'moodle_id' or key == 'question_id' :
                edited_data.at[w_count, key] = rec[key]                
                continue
            if w_en_lang == "X" and key == 'incorrect_feedback':
                edited_data.at[w_count, key] = rec[key]                
                continue
            if "\(" in rec[key]:
                w_latex = rec[key]
                w_latex = w_latex.replace('\(', "")
                w_latex = w_latex.replace('\)', "")                          
                st.latex(w_latex)
            if len(rec[key]) > 180:
                edited_data.at[w_count, key] = st.text_area(f"Row {w_count} - {key}", rec[key],  height=125)
            else:
                edited_data.at[w_count, key] = st.text_input(f"Row {w_count} - {key}", rec[key])
        w_count += 1
        st.divider()
    # data = pd.DataFrame(data)           #Convert the list of original data to a dataframe
    # for i in range(len(data)):
    #     for col in data.columns:
    #         if "\(" in data.at[i, col]:
    #             w_latex = data.at[i, col]
    #             w_latex = w_latex.replace('\(', "")
    #             w_latex = w_latex.replace('\)', "")                          
    #             st.latex(w_latex)
    #         if col == 'moodle_id':
    #             edited_data.at[i, col] = data.at[i, col]
    #             st.write('Question ID: ' + )
    #             #st.write(f"### {col}: {data.at[i, col]}")
    #             continue
    #         if len(data.at[i, col]) > 180:     #If the length of the data is more than 180 chars
    #             edited_data.at[i, col] = st.text_area(f"Row {i+1} - {col}", data.at[i, col],  height=125)
    #         else:
    #             edited_data.at[i, col] = st.text_input(f"Row {i+1} - {col}", data.at[i, col])   #Edits the data in the dataframe
    return edited_data


def create_xml(data,new_filename):
    if st.button("Please check and confirm the above changes"):
        input_table = data.to_dict('records')
        output_table = []
        for data in input_table:        
            data['questiontext'] = data['questiontext'].replace('\n', '<br>')
            data['option1'] = data['option1'].replace('\n', '<br>')
            data['option2'] = data['option2'].replace('\n', '<br>')
            data['option3'] = data['option3'].replace('\n', '<br>')
            data['option4'] = data['option4'].replace('\n', '<br>')
            data['soln'] = data['soln'].replace('\n', '<br>')
            data['incorrect_feedback'] = data['incorrect_feedback'].replace('\n', '<br>')
            output_table.append(data)

        # Remove the below code
        # test_table = []
        # for rec in output_table:
        #     if 'B10261' in rec['questiontext']:
        #         st.subheader(rec['soln'])
        #         test_table.append(rec)
        #         break
        # output_table = test_table
        # Remove the above code         

        xml_modified_data = create_moodle_xml(output_table)
        xml_data_utf8 = xml_modified_data.encode('utf-8')
        st.subheader("XML file has been created successfully!. Please click below button to download")
        st.download_button(
            label=" Click to Download XML File",
            data=xml_data_utf8,
            file_name=new_filename,
            mime="application/xml",
            key = "download_button"
            )
        
        # Add JavaScript to trigger download of the file
        # Add JavaScript to trigger download of the file
        # Add JavaScript to trigger download of the file
        # download_js = f"""
        # <script>
        # const blob = new Blob(["{xml_data_utf8}"], {{ type: "application/xml" }});
        # const url = URL.createObjectURL(blob);
        # const anchor = document.createElement('a');
        # anchor.href = url;
        # anchor.download = '{new_filename}';
        # document.body.appendChild(anchor);
        # anchor.click();
        # document.body.removeChild(anchor);
        # URL.revokeObjectURL(url);
        # </script>
        # """
        # st.markdown(download_js, unsafe_allow_html=True)
    #b64_encoded_xml = base64.b64encode(xml_tree.encode()).decode()
    #tree = f'<a href="data:application/xml;base64,{b64_encoded_xml}">Download XML</a>'
    #download_link = st.download_button("Save Changes and Download XML File", tree, file_name=new_filename, mime="application/xml")
    #Write the ElementTree object to an XML file mentioning path name
    #file_path = f"C:/Users/Taanya/Desktop/AssignGokul/Streamlit/{new_filename}"
    # file_path = f"C:/Moodle Files/Languages/{new_filename}"
    # with open(file_path, 'w', encoding='utf-8') as file:
    #     file.write(tree)
    #xml_string = ET.tostring(tree, encoding="utf-8")    
    #st.download_button(label="Save Changes and Download XML File ", data=tree, file_name=new_filename)

    #st.write("### Updated XML file has been created successfully!")


def compare_original_and_updated_data(xml_table, updated_data):
    user_data = updated_data.to_dict('records')
    st.write("### Updated Data:")
    w_count = 0
    w_changed = ""
    output = []
    for rec in xml_table:
        w_changed = ""
        # Replace space begin and end of the string
        rec['questiontext'] = rec['questiontext'].strip()
        rec['option1'] = rec['option1'].strip()
        rec['option2'] = rec['option2'].strip()
        rec['option3'] = rec['option3'].strip()
        rec['option4'] = rec['option4'].strip()
        rec['answer'] = rec['answer'].strip()
        rec['soln'] = rec['soln'].strip()
        rec['incorrect_feedback'] = rec['incorrect_feedback'].strip()
        if 'question_id' in rec:
            w_question_id = rec['question_id']
        else:  
            w_question_id = rec['moodle_id']
        for user_rec in user_data:
            # Replace space begin and end of the string
            user_rec['questiontext'] = user_rec['questiontext'].strip()
            user_rec['option1'] = user_rec['option1'].strip()
            user_rec['option2'] = user_rec['option2'].strip()
            user_rec['option3'] = user_rec['option3'].strip()
            user_rec['option4'] = user_rec['option4'].strip()
            user_rec['answer'] = user_rec['answer'].strip()
            user_rec['soln'] = user_rec['soln'].strip()
            if user_rec['soln'][-1] != '.':
                user_rec['soln'] = user_rec['soln'] + '.'
            user_rec['incorrect_feedback'] = user_rec['incorrect_feedback'].strip()
            
            if rec['moodle_id'] == user_rec['moodle_id']:
                if rec['questiontext'] != user_rec['questiontext']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f":red[Original Question Text : ]" + rec['questiontext'])
                    st.write(f':green[Updated Question Text : ]' + user_rec['questiontext'])
                    w_changed = "X"
                if rec['option1'] != user_rec['option1']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Option 1 : ]' + rec['option1'])
                    st.write(f':green[Updated Option 1 : ]' + user_rec['option1'])
                    w_changed = "X"
                if rec['option2'] != user_rec['option2']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Option 2 : ]' + rec['option2'])
                    st.write(f':green[Updated Option 2 : ]' + user_rec['option2'])
                    w_changed = "X"
                if rec['option3'] != user_rec['option3']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Option 3 : ]' + rec['option3'])
                    st.write(f':green[Updated Option 3 : ]' + user_rec['option3'])
                    w_changed = "X"
                if rec['option4'] != user_rec['option4']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Option 4 : ]' + rec['option4'])
                    st.write(f':green[Updated Option 4 : ]' + user_rec['option4'])
                    w_changed = "X"
                if rec['answer'] != user_rec['answer']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Answer : ]' + rec['answer'])
                    st.write(f':green[Updated Answer : ]' + user_rec['answer'])
                    w_changed = "X" 
                if rec['soln'] != user_rec['soln']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Solution : ]' + rec['soln'])
                    st.write(f':green[Updated Solution : ]' + user_rec['soln'])
                    w_changed = "X"
                if rec['incorrect_feedback'] != user_rec['incorrect_feedback']:
                    if w_changed == "":
                        st.write(f":blue[Below Changes were done for {w_question_id}]")
                    st.write(f':red[Original Incorrect Feedback : ]' + rec['incorrect_feedback'])
                    st.write(f':green[Updated Incorrect Feedback : ]' + user_rec['incorrect_feedback'])
                    w_changed = "X"
                
                if w_changed == "X":
                    w_count += 1
                    st.divider()
                
                
    if w_count == 0:
        st.write("No changes found in the data")
    else:
        st.subheader(f"Total {w_count} records have been changed")
        output.append('X')           
                
                
                # if rec['questiontext'] != user_rec['questiontext'] or rec['option1'] != user_rec['option1'] or rec['option2'] != user_rec['option2'] or rec['option3'] != user_rec['option3'] or rec['option4'] != user_rec['option4'] or rec['soln'] != user_rec['soln'] or rec['incorrect_feedback'] != user_rec['incorrect_feedback']:
                #    output.append(user_rec)

    return w_count
# Main
#st.header("Program to Update Quiz Data")
#st.title("Please upload XML file to display/edit the data")
xml_table, new_filename = get_data_from_xml()       #Get the data from the XML file
if len(xml_table) > 0 :
    #display_data(xml_table)                             #Display the original data
    updated_data = edit_data(xml_table)                 #Edit the data
    final_updated_data = compare_original_and_updated_data(xml_table, updated_data)
    if final_updated_data != 0:
        # st.write("### Updated Data:")
        # st.dataframe(final_updated_data)
        #xml_data = updated_data.to_dict('records')          #Converting the updated data dataframe to dictionary format
        create_xml(updated_data,new_filename)               #Once submitted, the updated XML file is created and saved in the folder path mentioned

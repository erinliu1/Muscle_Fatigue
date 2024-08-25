
def enable(button, styles=None):
    """
    Enables the button and applies the given style.
    """
    button.setEnabled(True)
    if styles:
        button.setStyleSheet(styles)
    
def disable(button, styles=None):
    """
    Disables the button and applies the given style.
    """
    button.setEnabled(False)
    if styles:
        button.setStyleSheet(styles)

def stylize_level_button(background_color, text_color, enabled=True):
    """
    Helper method to apply a consistent style to the level buttons
    """
    if enabled:
        return f"""
                QPushButton {{
                    background-color: {background_color};
                    border: 0.8px solid black;
                    border-radius: 10px;
                    padding: 3px;
                    width: 400px;
                    height: 18px;
                    font: 16px;
                    font-weight: bold;
                    color: {text_color};
                    text-align: left;
                    font-family: Courier New;
                }}
                QPushButton:hover {{
                    border: 3px solid black;
                }}
            """
    else:
        return f"""
                QPushButton {{
                    background-color: #CDCDCD;
                    border: 1px solid grey;
                    border-radius: 10px;
                    padding: 3px;
                    width: 400px;
                    height: 18px;
                    font: 16px;
                    font-weight: bold;
                    color: #949393;
                    text-align: left;
                    font-family: Courier New;
                }}
            """
    

button_styles = {
    'start/end button enabled': f"""
            QPushButton {{
                background-color: white;
                border: 1px solid black;
                border-radius: 2px;
                padding: 3px;
                height: 18px;
                font: 16px;
                font-weight: bold;
                color: black;
                text-align: center;
                font-family: Courier New;
            }}
            QPushButton:hover {{
                background-color: #B6B6B6;
            }}""",
    'start/end button disabled': f"""
            QPushButton {{
                background-color: #CDCDCD;
                border: 1px solid #949393;
                border-radius: 2px;
                padding: 3px;
                height: 18px;
                font: 16px;
                font-weight: bold;
                color: #949393;
                text-align: center;
                font-family: Courier New;
            }}""",
    'continue button enabled': f"""
                            QPushButton {{
                                background-color: white;
                                border: 2px solid black;
                                border-radius: 5px;
                                padding: 5px;
                                width: 500px;
                                height: 20px;
                                font: 18px;
                                color: black;
                                text-align: center;
                            }}
                            QPushButton:hover {{
                                background-color: #B6B6B6;
                            }}
                        """,
    'continue button disabled': f"""
            QPushButton {{
                background-color: #CDCDCD;
                border: 2px solid #949393;
                border-radius: 5px;
                padding: 5px;
                width: 500px;
                height: 20px;
                font: 18px;
                color: #949393;
                text-align: center;
            }}
        """,
    'imu button': f"""
            QPushButton {{
                background-color: #8CF0FF;
                border: 2px solid black;
                border-radius: 5px;
                padding: 5px;
                width: 500px;
                height: 20px;
                font: 18px;
                color: black;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #56ADBB;
            }}
        """,
    'submit button': f"""
            QPushButton {{
                background-color: white;
                border: 2px solid black;
                border-radius: 5px;
                padding: 5px;
                width: 500px;
                height: 20px;
                font: 18px;
                color: black;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #B6B6B6;
            }}
        """,
    

}

level_button_styles = {
            0: {
                'background_color': '#029B03',
                'text_color': 'white',
                'button_text': 'Nothing at all',
            },
            0.5 : {
                'background_color': '#22A70F',
                'text_color': 'white',
                'button_text': 'Extremely Low',
            },
            1 : {
                'background_color': '#41B41A',
                'text_color': 'white',
                'button_text': 'Very Low',
            },
            1.5 : {
                'background_color': '#61C026',
                'text_color': 'black',
                'button_text': '',
            },
            2: {
                'background_color': '#81CC31',
                'text_color': 'black',
                'button_text': 'Low',
            },
            2.5: {
                'background_color': '#A0D83D',
                'text_color': 'black',
                'button_text': '',
            },
            3: {
                'background_color': '#C0E548',
                'text_color': 'black',
                'button_text': 'Moderate',
            },
            3.5: {
                'background_color': '#DFF154',
                'text_color': 'black',
                'button_text': '',
            },
            4: {
                'background_color': '#FFFD5F',
                'text_color': 'black',
                'button_text': 'Somewhat high',
            },
            4.5: {
                'background_color': '#FFDE59',
                'text_color': 'black',
                'button_text': '',
            },
            5: {
                'background_color': '#FFBD59',
                'text_color': 'black',
                'button_text': 'High',
            },
            5.5: {
                'background_color': '#FFA753',
                'text_color': 'black',
                'button_text': '',
            },
            6: {
                'background_color': '#FF914D',
                'text_color': 'black',
                'button_text': '',
            },
            6.5: {
                'background_color': '#FF7452',
                'text_color': 'black',
                'button_text': '',
            },
            7: {
                'background_color': '#FF5757',
                'text_color': 'white',
                'button_text': 'Very high',
            },
            7.5: {
                'background_color': '#D54949',
                'text_color': 'white',
                'button_text': '',
            },
            8: {
                'background_color': '#AA3A3A',
                'text_color': 'white',
                'button_text': '',
            },
            8.5: {
                'background_color': '#802C2C',
                'text_color': 'white',
                'button_text': '',
            },
            9: {
                'background_color': '#551D1D',
                'text_color': 'white',
                'button_text': '',
            },
            9.5: {
                'background_color': '#2B0F0F',
                'text_color': 'white',
                'button_text': 'Extremely high',
            },
            10: {
                'background_color': 'black',
                'text_color': 'white',
                'button_text': 'Maximum',
            },
        }

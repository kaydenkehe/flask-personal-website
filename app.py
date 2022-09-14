from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from selenium.webdriver.firefox.options import Options
from os import listdir, path, mkdir, popen
from shutil import make_archive, rmtree
from selenium import webdriver
from bs4 import BeautifulSoup
from hash import hash


# --- CONFIG / VARIABLES ---


# Salts are appended to passwords before they are hashed as an extra layer of security
salts = ['D90GHL', 'M18XUJ', 'K62QTF']
# These are the actual hashed passwords to check the user inputted passwords against
actual_pwds = ['8858d100607b689dd1afa0c4a92448cf819ed6c4144805da48e5d93f995d0608ec7adfe2d768601525e2869a59d9b477bc33c050079245ac81c346b9c1167597',
                'e1321146ee11e098b235e860361c8a5f66e25ef395319f54cf7b76d074b137e067c6f27f44585b2afdca41cf0ee04cdc51cec1b7f052bfaa261b3fbfb33915c8',
                '4c10fdcec3c47ece7fe1739cac529b21062557f4723b675c70c892acfc7a3f2b21a128ccddb7c53273ff91eb0f31fcfaf1b93f5be5114f8d513e2c5f4139d760']

# Create instance of Flask class
app = Flask(__name__)
# Secret key helps protect cookies from being edited by user
app.config['SECRET_KEY'] = 'YOU DONT GET TO KNOW HANNAH'

# Colors used in website [Background, Background 2, Main Color, Main Highlighted]
colors = []
with open('static/colors.txt', 'r') as color_file:
    colors = color_file.read().split('\n')


# --- LOGIN PAGE ---


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_pwds = []
        # Checks if user entered passwords are correct
        # If so, set logged_in cookie and redirect to home page
        for i in range(3): user_pwds.append(request.form[f'pwd{i + 1}'])
        if hash(user_pwds, salts) == actual_pwds:
            session['logged_in'] = True
            return redirect(url_for('home'))

        return redirect(url_for('login'))
    return render_template('login.html', colors=colors)

# If user doesn't specify page, redirect them to login page
@app.route('/')
def no_dir(): return redirect(url_for('login'))


# --- HOME PAGE ---


@app.route('/home')
def home():
    # This verifies that the user is logged in before rendering the page
    if session.get('logged_in'): return render_template('home.html', colors=colors)
    return redirect(url_for('login'))


# --- NAS PAGE ---


# What directory we are on INSIDE of the NAS_Storage directory
filepath = ''
# Main NAS storage directory location
#nas_dir = '/home/pi/WebsiteFlask/static/NAS_Storage/' # Linux
nas_dir = 'C:/Users/kayde/Desktop/Projects/PersonalWebsite/WebsiteFlask/static/NAS_Storage/' # Windows

# List of files on NAS_Storage directory
files = listdir(nas_dir)
# Used to determine what icon would match a particular file
icon_file_names = []

@app.route('/nas', methods=['POST', 'GET'])
def nas():
    global filepath, files, icon_file_names
    if session.get('logged_in'):
        icon_file_names = []

        if request.method == 'POST':
            # Checks to see if the button the user clicked on represents a file
            if request.form['submit_button'] in files:
                file_name = request.form['submit_button']

                # Handles navigating through directories when the user clicks on a folder
                if path.isdir(nas_dir + filepath + file_name):
                    filepath += f"{file_name}/"
                    files = listdir(nas_dir + filepath)

                # Handles downloading a file if the user clicks on it
                elif path.isfile(nas_dir + filepath + file_name):
                    #return send_file('static/NAS_Storage/' + filepath + file_name, as_attachment=True) # Linux
                    return send_file('static\\NAS_Storage\\' + filepath.replace('/', '\\') + file_name, as_attachment=True) # Windows

            # Handles moving backwards through the directories using the back button
            elif request.form['submit_button'] == '<':
                if filepath != '':
                    if filepath.count('/') > 1: filepath = filepath[:len(filepath) - 1 - filepath[::-1][1:].find('/')]
                    else: filepath = ''
                    files = listdir(nas_dir + filepath)

            # Handles new directory creation
            elif request.form['submit_button'] == 'Create Directory':
                dir_name = request.form['dir_name_input']
                if dir_name != '' and dir_name.count('/') == 0:
                    mkdir(nas_dir + filepath + dir_name)
                    files = listdir(nas_dir + filepath)
                else: flash('Invalid directory name')

            # Handles downloading entire current directory
            elif request.form['submit_button'] == 'Download Directory':
                # Deletes and then remakes NAS_Storage_Zip folder so it doesn't take up too much space
                #rmtree('/home/pi/WebsiteFlask/static/NAS_Storage_Zip') # Linux
                #mkdir('/home/pi/WebsiteFlask/static/NAS_Storage_Zip') # Linux
                rmtree('C:/Users/kayde/Desktop/Projects/PersonalWebsite/WebsiteFlask/static/NAS_Storage_Zip') # Windows
                mkdir('C:/Users/kayde/Desktop/Projects/PersonalWebsite/WebsiteFlask/static/NAS_Storage_Zip') # Windows
                
                folder_name = ''
                if filepath == '': folder_name = 'NAS'
                elif filepath.count('/') == 1: folder_name = filepath[:-1]
                else: folder_name = filepath[::-1][:filepath[::-1].index('/', filepath[::-1].index('/') + 1)][::-1][:-1] # I am truly sorry

                # Creates zip folder from directory, then downloads it
                #make_archive(f'/home/pi/WebsiteFlask/static/NAS_Storage_Zip/{folder_name}', 'zip', nas_dir + filepath) # Linux
                #return send_file(f'/home/pi/WebsiteFlask/static/NAS_Storage_Zip/{folder_name}.zip', as_attachment=True) # Linux
                make_archive(f'C:/Users/kayde/Desktop/Projects/PersonalWebsite/WebsiteFlask/static/NAS_Storage_Zip/{folder_name}', 'zip', nas_dir + filepath) # Windows
                return send_file(f'static\\NAS_Storage_Zip\\{folder_name}.zip', as_attachment=True) # Windows

            # Handles file upload
            elif request.form['submit_button'] == 'Upload':
                file = request.files['file_upload']
                if request.files['file_upload']:
                    file.save(nas_dir + filepath + file.filename)
                    files = listdir(nas_dir + filepath)

            # Handles home button
            elif request.form['submit_button'] == '':
                return redirect(url_for('home'))

        # Make list of icons based on file types
        for file in files:
            if file.count('.') == 0: icon_file_names.append('folder_icon.png')
            elif '.jpeg' in file.lower() or '.png' in file.lower() or 'jpg' in file.lower(): icon_file_names.append('image_icon.png')
            else: icon_file_names.append('file_icon.png')

        return render_template('nas.html', files=files, files_len=len(files), filepath=filepath, icon_file_names=icon_file_names, colors=colors)
    return redirect(url_for('login'))


# -- PROXY PAGE ---


@app.route('/proxy', methods=['POST', 'GET'])
def proxy():
    if session.get('logged_in'):
        if request.method == 'POST':
            # Checks if user pressed 'Go' button
            if request.form['submit_button'] == 'Go':
                url = request.form['url_input']
                if url != '':
                    try:
                        # Render page, download source code, and write it to proxy_page.html, which is displayed in proxy.html
                        options = Options()
                        options.headless = True
                        #driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options) # Linux
                        driver = webdriver.Firefox(options=options) # Windows
                        driver.get(url)
                        page_code = BeautifulSoup(driver.page_source, 'html.parser')
                        driver.close()
                        with open('templates/proxy_page.html', 'w', encoding='utf-8') as proxy_page: proxy_page.write('{% raw %}' + str(page_code.prettify()) + '{% endraw %}')
                    except:
                        try: driver.close()
                        except: pass

            # Handles home button
            elif request.form['submit_button'] == '':
                return redirect(url_for('home'))

            # Handles back button, which just clears the current page
            elif request.form['submit_button'] == '<':
                with open('templates/proxy_page.html', 'w', encoding='utf-8') as _: pass

        # Clear proxy_page.html if the user performs a GET request (loads the page)
        else:
            with open('templates/proxy_page.html', 'w', encoding='utf-8') as _: pass

        return render_template('proxy.html', colors=colors)
    return redirect(url_for('login'))


# --- GAMES PAGE ---


# Creats list of the names of every game
game_list = listdir('templates/game_pages')
game_list.sort()
# Which game is being played right now
active_game = '!blank'

@app.route('/games', methods=['POST', 'GET'])
def games():
    global active_game
    if session.get('logged_in'):
        if request.method == 'POST':

            # Handles home button
            if request.form['submit_button'] == '':
                return redirect(url_for('home'))

            # Clears game when back button is pressed
            elif request.form['submit_button'] == '<': active_game = '!blank'

            # Changes active game when a game button is pressed
            else: active_game = request.form['submit_button']

        return render_template('games.html', game_list=game_list[1:], active_game=f'game_pages/{active_game}.html', colors=colors)
    return redirect(url_for('login'))


# --- TERMINAL PAGE ---


inputs = []
outputs = []
@app.route('/terminal', methods=['POST', 'GET'])
def ssh():
    global inputs, outputs
    if session.get('logged_in'):
        if request.method == 'POST':
            # Handles home button
            if request.form['submit_button'] == '':
                return redirect(url_for('home'))

            # Handles user inputted commands
            elif request.form['submit_button'] == '>':
                user_command = request.form['command_input']
                if user_command == 'clear':
                    inputs = []
                    outputs = []

                else:
                    inputs.append('> ' + user_command)
                    # This executes the command and appends its output to the output array
                    outputs.append(popen(user_command + ' 2>&1').read())

        return render_template('terminal.html', inputs=inputs, outputs=outputs, dict_length=len(inputs), colors=colors)
    return redirect(url_for('login'))


# --- SETTINGS PAGE ---


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    global colors
    if session.get('logged_in'):
        if request.method == 'POST':

            #Handles home button
            if request.form['submit_button'] == '':
                return redirect(url_for('home'))

            # Handles submitting colors and writing them to color file
            elif request.form['submit_button'] == 'Submit':
                colors = [request.form[f'color{i}'] for i in range(4)]
                with open('static/colors.txt', 'w') as color_file:
                    for i in colors: color_file.write(i + '\n')

        return render_template('settings.html', colors=colors)
    return redirect(url_for('login'))


# --- RUN WEBSITE ---


# Run website on port 8080 on current machine
if __name__=='__main__': app.run(debug=True, port=8080, host='0.0.0.0')

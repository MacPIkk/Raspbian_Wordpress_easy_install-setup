import os

# Define some colors to use
TBLUE =  '\033[1;34m' # blue Text
ENDC = '\033[m' # defaults
#-----------------------------------------

# Prompt for custom configuration
print(TBLUE + "Adduser for mysql", ENDC)
username = input("username : ")
password = input("password : ")


print(TBLUE + "The domain name you want to set up for the wordpress site", ENDC)
domain_name = input("domain_name (example.com) : ")

print(TBLUE + "the name you want to give to the apache conf file which links to your site folder", ENDC)
conf_file_name = input("conf file name : ")

print(TBLUE + "the name you want to give to the site s folder name", ENDC)
wp_folder_name = input("wordpress folder name : ")

print(TBLUE + "The name you want to give to the database of the wordpress site", ENDC)
db_name = input("database name : ")

#-----------------------------------------

# initialize files that will be used
bash_file = open("wp_setup.bash", "w+")
os.chmod("wp_setup.bash", 0o755)

conf_file = open( (conf_file_name + ".conf"), "w+")
os.chmod((conf_file_name + ".conf"), 0o755)

sql_file = open("setup_db_with_user.sql", "w+")
os.chmod("setup_db_with_user.sql", 0o755)


final_script_to_exec = open("execute_all_scripts.bash", "w+")
os.chmod("execute_all_scripts.bash", 0o755)
#-----------------------------------------

# tiny functions that will be used to write into files
def add_line_break(int, file):
    for x in range (int):
        file.write("\n")


def add_text_to_file(text, file,int_line_break):
    file.write(text)
    add_line_break(int_line_break, file)
#-----------------------------------------

# Create sql file that will be executed to create database, user and grant database's permissions to the user
def create_sql_file():
    add_text_to_file(("CREATE DATABASE " + db_name + ";"), sql_file, 1)
    add_text_to_file(("CREATE USER " + "'" + username + "'@'localhost' IDENTIFIED BY '" + password + "';"), sql_file, 1)
    add_text_to_file(("GRANT ALL PRIVILEGES on " + db_name + ".* TO '" + username + "'@'localhost' IDENTIFIED BY '" + password + "';"), sql_file, 1)
    add_text_to_file("FLUSH PRIVILEGES;", sql_file, 1)
    add_text_to_file("EXIT;", sql_file, 1)
#-----------------------------------------

# Create bash file to :
def create_main_file():
    # update repository sources and isntall requirements packages :  apache2, mysql, php with extensions
    add_text_to_file("#!/bin/bash", bash_file, 3)
    add_text_to_file("sudo apt-get update", bash_file, 1)
    add_text_to_file("echo Y | sudo apt install php7.4", bash_file, 1)
    add_text_to_file("echo Y | sudo apt install php7.4-mysql", bash_file, 1)
    add_text_to_file("echo Y | sudo apt install default-mysql-server", bash_file, 1)
    #-------------------------

    # download wordpress files archive and extract the folder
    add_text_to_file("wget -c https://wordpress.org/latest.tar.gz", bash_file, 1)
    add_text_to_file("tar -xvzf latest.tar.gz", bash_file, 1)
    #-------------------------

    # put wordpress folder into the right place, change owner and set permissions
    add_text_to_file(("sudo mv wordpress/ /var/www/html/" + wp_folder_name),bash_file, 1)
    add_text_to_file(("sudo chown -R www-data:www-data /var/www/html/"+ wp_folder_name +"/"), bash_file, 1)
    add_text_to_file(("sudo chmod 755 -R /var/www/html/" + wp_folder_name), bash_file, 1)
    #-------------------------

    # put apache2 conf file to the right place, and enable the conf
    add_text_to_file(("sudo mv "+ conf_file_name + ".conf /etc/apache2/sites-available/" + conf_file_name + ".conf"), bash_file, 1)
    add_text_to_file(("sudo ln -s /etc/apache2/sites-available/" + conf_file_name + ".conf /etc/apache2/sites-enabled/" + conf_file_name + ".conf"), bash_file, 1)
    add_text_to_file(("sudo a2enmod rewrite"), bash_file, 1)
    add_text_to_file(("sudo a2ensite " + conf_file_name), bash_file, 1)
    #-------------------------

    # execute the sql file
    add_text_to_file("sudo mysql -u root  < ./setup_db_with_user.sql", bash_file, 1)
    #--------------------------
    # then restart apache2 service
    add_text_to_file(("sudo systemctl restart apache2"), bash_file, 1)
    #-----------------------------------------

    # Delete temporary files
    add_text_to_file(("sudo rm wp_setup.bash setup_db_with_user.sql execute_all_scripts.bash "), bash_file, 1)
    #---------------------------------------


# Create apache2 VirtualHost configuration file
def create_conf_file():
    add_text_to_file("<VirtualHost *:80>", conf_file, 1)
    add_text_to_file(("      ServerAdmin admin@" + domain_name  ), conf_file, 1)
    add_text_to_file(("      DocumentRoot /var/www/html/" + wp_folder_name), conf_file, 1)
    add_text_to_file(("      ServerName " + domain_name), conf_file,1)
    add_text_to_file(("      <Directory /var/www/html/" + wp_folder_name + ">"), conf_file, 1)
    add_text_to_file(("                Options FollowSymlinks"), conf_file, 1)
    add_text_to_file(("                AllowOverride All"), conf_file, 1)
    add_text_to_file(("                Require all granted"), conf_file, 1)
    add_text_to_file(("      </Directory>"), conf_file, 1)
    add_text_to_file(("      ErrorLog ${APACHE_LOG_DIR}/your-domain.com_error.log"), conf_file, 1)
    add_text_to_file(("      CustomLog ${APACHE_LOG_DIR}/your-domain.com_access.log combined"), conf_file, 1)
    add_text_to_file(("</VirtualHost>"), conf_file, 1)
#-----------------------------------------

# Create the final script that will execute the created file
def create_final_script():
    add_text_to_file("sudo ./wp_setup.bash", final_script_to_exec, 1)

#-----------------------------------------

# Execute the functions above
create_conf_file()
create_sql_file()
create_main_file()
create_final_script()
#-----------------------------------------

print(TBLUE + "then you have to execute the main setup file by : sudo ./execute_all_scripts.bash", ENDC)

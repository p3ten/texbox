import os
import subprocess

# Remove Server Version Banner
httpd_conf_path = "/etc/apache2/conf-available/security.conf"
os.system(f"sed -i 's/^ServerTokens .*/ServerTokens Prod/g' {httpd_conf_path}")
os.system(f"sed -i 's/^ServerSignature .*/ServerSignature Off/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Disable directory browser listing
htdocs_path = "/var/www/html"
os.system(f"sed -i '/<Directory {htdocs_path}>/,/<\\/Directory>/s/Options Indexes/Options -Indexes/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Etag
os.system(f"sed -i 's/^FileETag .*/FileETag None/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Run Apache from a non-privileged account
os.system("groupadd apache")
os.system("useradd -g apache apache")
os.system("chown -R apache:apache /opt/apache")
os.system(f"sed -i 's/^User .*/User apache/g' {httpd_conf_path}")
os.system(f"sed -i 's/^Group .*/Group apache/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Protect binary and configuration directory permission
os.system(f"chmod -R 750 {htdocs_path}bin {htdocs_path}conf")

# System Settings Protection
os.system(f"sed -i '/<Directory \\/>/,/<\\/Directory>/s/AllowOverride .*/AllowOverride None/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# HTTP Request Methods
os.system(f"sed -i '/<Directory {htdocs_path}>/,/<\\/Directory>/s/<\\/Directory>/\\t<LimitExcept GET POST HEAD>\\n\\t\\tdeny from all\\n\\t<\\/LimitExcept>\\n<\\/Directory>/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Disable Trace HTTP Request
os.system(f"sed -i 's/^TraceEnable .*/TraceEnable Off/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Set HttpOnly and Secure flags for cookies
subprocess.run(["sudo", "sed", "-i", 's/^#LoadModule headers_module/LoadModule headers_module/', "/etc/apache2/conf-available/security.conf"])
subprocess.run(["sudo", "sed", "-i", 's/^#LoadModule rewrite_module/LoadModule rewrite_module/', "/etc/apache2/conf-available/security.conf"])
subprocess.run(["sudo", "sed", "-i", "/<IfModule headers_module>/a Header edit Set-Cookie ^(.*)$ $1;HttpOnly;Secure", "/etc/apache2/conf-available/security.conf"])

# Set X-Frame-Options to SAMEORIGIN
subprocess.run(["sudo", "sed", "-i", 's/^#LoadModule headers_module/LoadModule headers_module/', "/etc/apache2/conf-available/security.conf"])
subprocess.run(["sudo", "sed", "-i", "/<IfModule headers_module>/a Header always set X-Frame-Options \"SAMEORIGIN\"", "/etc/apache2/conf-available/security.conf"])

# Add X-Frame-Options directive to httpd.conf
with open('/etc/apache2/conf-available/security.conf', 'a') as f:
    f.write('\n<IfModule headers_module>\n')
    f.write('Header always set X-Frame-Options "SAMEORIGIN"\n')
    f.write('</IfModule>\n')

# Path to the httpd.conf file
httpd_conf_path = "/etc/apache2/conf-available/security.conf"

# Open the httpd.conf file using vi and search for the Directory block
subprocess.run(["vi", "+/Directory", httpd_conf_path])

# Add the Includes option to the Options directive inside the Directory block
with open(httpd_conf_path, "r") as f:
    lines = f.readlines()

with open(httpd_conf_path, "w") as f:
    for line in lines:
        if line.strip().startswith("<Directory"):
            f.write(line)
            f.write("    Options -Indexes -Includes\n")
        else:
            f.write(line)

# Restart the web server to apply the changes
#subprocess.run(["systemctl", "restart", "httpd"])
   
    
# Disable SSI in httpd.conf
#with open('/etc/apache2/conf-available/security.conf', 'r') as f:
#    conf_lines = f.readlines()

#with open('/etc/apache2/conf-available/security.conf', 'w') as f:
#    for line in conf_lines:
#        if '<Directory /opt/apache/htdocs>' in line:
#            line = line.rstrip() + ' -IncludesNOEXEC\n'
#        f.write(line)

# Add X-XSS-Protection header to httpd.conf
with open('/etc/apache2/conf-available/security.conf', 'a') as f:
    f.write('\n<IfModule headers_module>\n')
    f.write('Header always set X-XSS-Protection "1; mode=block"\n')
    f.write('</IfModule>\n')

# Disable HTTP 1.0 protocol using mod_rewrite
with open('/etc/apache2/conf-available/security.conf', 'r') as f:
    conf_lines = f.readlines()

with open('/etc/apache2/conf-available/security.conf', 'w') as f:
    for line in conf_lines:
        if 'LoadModule rewrite_module modules/mod_rewrite.so' in line:
            line = line.rstrip() + '\n'
        elif 'RewriteEngine On' in line:
            continue
        elif '<VirtualHost' in line:
            line = line.rstrip() + '\n\nRewriteEngine On\nRewriteCond %{THE_REQUEST} !HTTP/1.1$\nRewriteRule .* - [F]\n\n'
        f.write(line)

# Set timeout value to 60 seconds
with open('/etc/apache2/conf-available/security.conf', 'a') as f:
    f.write('\nTimeout 60\n')

# Update software repos
os.system("sudo apt update -y")

# Install ModSecurity Apache module
os.system("sudo apt install libapache2-mod-security2")
os.system("echo 'Y' | sudo apt install libapache2-mod-security2")

# Check version of installed software
os.system("apt-cache show libapache2-mod-security2")

# Configure ModSecurity
os.system("cp /etc/modsecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf")
os.system("nano /etc/modsecurity/modsecurity.conf")  # Edit the configuration file manually
os.system("service apache2 restart")

# Download OWASP Core Rule Set
os.system("wget https://github.com/coreruleset/coreruleset/archive/v3.3.0.zip")
os.system("unzip v3.3.0.zip")
os.system("mv coreruleset-3.3.0/crs-setup.conf.example /etc/modsecurity/crs-setup.conf")
os.system("mv coreruleset-3.3.0/rules/ /etc/modsecurity/")

# Edit Apache security2.conf file
# os.system("sudo nano /etc/apache2/mods-enabled/security2.conf")
# Ensure both the default ModSecurity and new CRS configuration files are listed
os.system("echo 'IncludeOptional /etc/modsecurity/*.conf' | sudo tee -a /etc/apache2/mods-enabled/security2.conf")
os.system("echo 'Include /etc/modsecurity/rules/*.conf' | sudo tee -a /etc/apache2/mods-enabled/security2.conf")
os.system("service apache2 restart")

import os
import subprocess

# Remove Server Version Banner
httpd_conf_path = "/etc/apache2/conf-available/security.conf"
os.system(f"sed -i 's/^ServerTokens .*/ServerTokens Prod/g' {httpd_conf_path}")
os.system(f"sed -i 's/^ServerSignature .*/ServerSignature Off/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Disable directory browser listing
htdocs_path = "/var/www/html"
os.system(f"mkdir {htdocs_path}/test")
os.system(f"touch {htdocs_path}/test/hi")
os.system(f"touch {htdocs_path}/test/hello")
os.system(f"sed -i '/<Directory {htdocs_path}>/,/<\\/Directory>/s/Options Indexes/Options -Indexes/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Etag
os.system(f"sed -i 's/^FileETag .*/FileETag None/g' {httpd_conf_path}")
#os.system("service apache2 restart")

# Run Apache from a non-privileged account
os.system("groupadd apache")
os.system("useradd -g apache -d /opt/apache -s /bin/false apache")
os.system("chown -R apache:apache /opt/apache")
os.system(f"sed -i 's/^User .*/User apache/g' {httpd_conf_path}")
os.system(f"sed -i 's/^Group .*/Group apache/g' {httpd_conf_path}")

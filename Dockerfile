FROM httpd:2.4

# Copy your static site content
COPY . /usr/local/apache2/htdocs/

# Enable mod_rewrite and headers
RUN sed -i '/LoadModule rewrite_module/s/^#//g' /usr/local/apache2/conf/httpd.conf && \
    sed -i '/LoadModule headers_module/s/^#//g' /usr/local/apache2/conf/httpd.conf

# Harden Apache config
RUN sed -i 's/Options Indexes FollowSymLinks/Options -Indexes +FollowSymLinks/' /usr/local/apache2/conf/httpd.conf && \
    echo 'ServerSignature Off' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'ServerTokens Prod' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'Header set X-Content-Type-Options "nosniff"' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'Header always append X-Frame-Options SAMEORIGIN' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'Header set X-XSS-Protection "1; mode=block"' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'Header set Referrer-Policy "strict-origin-when-cross-origin"' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'Header set Permissions-Policy "geolocation=(), camera=(), microphone=()"' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'ErrorDocument 403 /error/403.html' >> /usr/local/apache2/conf/httpd.conf && \
    echo 'ErrorDocument 404 /error/404.html' >> /usr/local/apache2/conf/httpd.conf

# Allow .htaccess to override settings (needed for clean URLs)
RUN sed -i '/<Directory "\/usr\/local\/apache2\/htdocs">/,/<\/Directory>/s/AllowOverride None/AllowOverride All/' /usr/local/apache2/conf/httpd.conf

# Copy the .htaccess file (handles .html hiding + 403/404 logic)
COPY .htaccess /usr/local/apache2/htdocs/.htaccess

EXPOSE 80
CMD ["httpd-foreground"]

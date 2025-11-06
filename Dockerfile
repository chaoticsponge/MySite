FROM httpd:2.4

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      python3 \
      python3-yaml \
      nodejs \
      npm \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /usr/local/bin/supercronic "${SUPERCRONIC_URL}" && \
    chmod +x /usr/local/bin/supercronic

# Copy your static site content
COPY . /usr/local/apache2/htdocs/

RUN install -Dm755 /usr/local/apache2/htdocs/scripts/update_letterboxd.sh /usr/local/bin/update_letterboxd.sh && \
    install -Dm644 /usr/local/apache2/htdocs/cron/letterboxd.cron /etc/supercronic/letterboxd.cron && \
    install -Dm755 /usr/local/apache2/htdocs/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Install Letterboxd CLI dependencies
RUN cd /usr/local/apache2/htdocs/letterboxd && npm install --production

# Enable mod_rewrite and headers
RUN sed -i '/LoadModule rewrite_module/s/^#//g' /usr/local/apache2/conf/httpd.conf && \
    sed -i '/LoadModule headers_module/s/^#//g' /usr/local/apache2/conf/httpd.conf

# Harden Apache config
RUN echo 'ServerName localhost' >> /usr/local/apache2/conf/httpd.conf && \
    sed -i 's/Options Indexes FollowSymLinks/Options -Indexes +FollowSymLinks/' /usr/local/apache2/conf/httpd.conf && \
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

EXPOSE 80
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["httpd-foreground"]

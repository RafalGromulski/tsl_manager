# Use the official Nginx base image
FROM nginx:1.27-alpine

# Prepare write directories (you'll give them tmpfs in runtime anyway, but let them exist)
RUN mkdir -p /var/cache/nginx /var/run /tmp

# Overwrite main configuration WITHOUT 'user' (silences warning)
COPY ./nginx.conf /etc/nginx/nginx.conf

# Copy the custom Nginx configuration file into the container
COPY ./default.conf /etc/nginx/conf.d/default.conf

ENV NGINX_ENTRYPOINT_QUIET_LOGS=1

# Expose the default port the app listens on
EXPOSE 8080

STOPSIGNAL SIGQUIT

# Run as non-root (compatible with read_only + tmpfs in compose)
USER nginx

# Start Nginx in the foreground
CMD ["sh","-lc","exec nginx -g 'daemon off;'"]

# Use the official Nginx base image
FROM nginx:1.25.5

# Set the working directory inside the container
WORKDIR /etc/nginx

# Copy the custom Nginx configuration file into the container
COPY ./default.conf /etc/nginx/conf.d/default.conf

# Expose the default port the app listens on
EXPOSE 8080

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]

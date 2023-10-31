FROM nginx:1.23

# Replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Import static files
COPY static/ /static
COPY api_errors/ /api_errors

# Nginx debug mode
CMD ["nginx", "-g", "daemon off;"]
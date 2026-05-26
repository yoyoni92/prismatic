FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["/bin/sh", "-c", \
  "echo 'window.PRISMATIC_CONFIG={};' > /usr/share/nginx/html/config.js \
   && nginx -g 'daemon off;'"]

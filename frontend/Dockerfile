FROM node:18-alpine as builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
ARG REACT_APP_BASE_URL
ENV REACT_APP_BASE_URL=$REACT_APP_BASE_URL
COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine
RUN apk add --no-cache gettext

COPY --from=builder /app/build /usr/share/nginx/html

# Create nginx config - proxy API calls to backend so POSTs reach FastAPI
RUN echo 'server {' > /etc/nginx/conf.d/default.conf.template && \
    echo '    listen ${PORT};' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    # Proxy API endpoints to backend' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    location /chat/ {' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_pass http://backend:8000/chat/;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_http_version 1.1;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Forwarded-Proto $scheme;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header Connection "";' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_buffering off;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    }' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    location /process_audio/ {' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_pass http://backend:8000/process_audio/;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_http_version 1.1;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Forwarded-Proto $scheme;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header Connection "";' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_buffering off;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    }' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    location /api/ {' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_pass http://backend:8000/api/;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_http_version 1.1;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header X-Forwarded-Proto $scheme;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_set_header Connection "";' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        proxy_buffering off;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    }' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    # Serve frontend' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        try_files $uri /index.html;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    }' >> /etc/nginx/conf.d/default.conf.template && \
    echo '}' >> /etc/nginx/conf.d/default.conf.template

EXPOSE 8080
ENV PORT=8080
CMD ["sh", "-c", "envsubst '${PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]

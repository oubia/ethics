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

# Create nginx template
RUN printf 'server {\n  listen ${PORT};\n  location / {\n    root /usr/share/nginx/html;\n    try_files $$uri /index.html;\n  }\n}\n' > /etc/nginx/conf.d/default.conf.template

EXPOSE 8080
ENV PORT=8080
CMD ["sh", "-c", "envsubst < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]

FROM node:18-alpine as builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
ARG REACT_APP_BASE_URL
ENV REACT_APP_BASE_URL=$REACT_APP_BASE_URL
COPY . .
RUN npm run build

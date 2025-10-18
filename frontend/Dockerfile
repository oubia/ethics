FROM node:18-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
ARG REACT_APP_BASE_URL
ENV REACT_APP_BASE_URL=$REACT_APP_BASE_URL
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

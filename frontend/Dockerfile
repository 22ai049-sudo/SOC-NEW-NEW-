FROM node:20-alpine
WORKDIR /app

ARG NPM_REGISTRY=
COPY package.json vite.config.js index.html ./
COPY src ./src

RUN if [ -n "$NPM_REGISTRY" ]; then npm config set registry "$NPM_REGISTRY"; fi \
    && npm config delete proxy || true \
    && npm config delete https-proxy || true \
    && npm install --no-audit --no-fund

EXPOSE 3000
CMD ["npm", "run", "dev"]

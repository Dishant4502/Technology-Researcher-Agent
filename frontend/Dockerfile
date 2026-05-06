# ──────────────────────────────────────────────
# Stage 1 – node builder: compile the Vite app
# ──────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy manifests first for layer-cache friendliness
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

COPY . .

# Inject the runtime API base at build time (can be overridden via --build-arg)
# ARG VITE_API_BASE=http://localhost:8000/api
ARG VITE_API_BASE=http://3.87.112.2:8000/api
ENV VITE_API_BASE=${VITE_API_BASE}

RUN npm run build

# ──────────────────────────────────────────────
# Stage 2 – nginx: serve the static bundle
# ──────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config (Single-Page App routing)
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy compiled assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]

FROM golang:1.23-alpine AS builder

WORKDIR /app

# 安裝基本工具
RUN apk add --no-cache protobuf-dev

# 複製 go.mod 和 go.sum
COPY go.mod go.sum* ./
RUN go mod download

# 複製源代碼
COPY . .

# 編譯應用
RUN go build -o /app/robot-tracker ./cmd/server

# 使用輕量級的 alpine 映像
FROM alpine:latest

WORKDIR /app

# 從 builder 階段複製編譯後的二進制文件
COPY --from=builder /app/robot-tracker .

# 創建非 root 用戶
RUN adduser -D appuser
USER appuser

# 暴露 gRPC 端口
EXPOSE 50051

# 執行應用
CMD ["./robot-tracker"]
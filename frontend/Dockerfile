# 開發用 base image
FROM node:18-alpine

# 設定工作目錄
WORKDIR /app

# 複製 package 檔案並安裝
COPY package*.json ./
RUN npm install

# 最後使用 docker-compose 掛 volume，不要複製全部代碼

# 啟動開發模式
CMD ["npm", "run", "dev"]

package main

import (
    "fmt"
    "net"
    "os"
    "os/signal"
    "syscall"

    "google.golang.org/grpc"

    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/config"
    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/position"
    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/service"
    "github.com/tetsufromtw/practice-robot/robot-tracker/pkg/logger"
    "github.com/tetsufromtw/practice-robot/robot-tracker/proto"
)

func main() {
    // 初始化配置
    cfg := config.NewDefaultConfig()

    // 初始化日誌
    log := logger.NewSimpleLogger()

    // 創建位置生成器
    generator := position.NewRandomGenerator(cfg)

    // 創建服務實例
    trackerService := service.NewRobotTrackerService(cfg, generator, log)

    // 監聽指定端口
    address := fmt.Sprintf(":%s", cfg.Port)
    lis, err := net.Listen("tcp", address)
    if err != nil {
        log.Error("無法監聽端口: %v", err)
        os.Exit(1)
    }

    // 創建 gRPC 服務器
    grpcServer := grpc.NewServer()

    // 註冊服務
    proto.RegisterRobotTrackerServer(grpcServer, trackerService)

    // 處理優雅關閉
    go func() {
        c := make(chan os.Signal, 1)
        signal.Notify(c, os.Interrupt, syscall.SIGTERM)
        <-c
        log.Info("接收到關閉信號，正在關閉服務...")
        grpcServer.GracefulStop()
    }()

    // 啟動服務器
    log.Info("robot-tracker 服務啟動於 %s", address)
    if err := grpcServer.Serve(lis); err != nil {
        log.Error("服務器出錯: %v", err)
        os.Exit(1)
    }
}
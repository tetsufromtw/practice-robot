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
    // 設定を初期化
    cfg := config.NewDefaultConfig()

    // ロガーを初期化
    log := logger.NewSimpleLogger()

    // 位置生成器を作成
    generator := position.NewRandomGenerator(cfg)

    // サービスインスタンスを作成
    trackerService := service.NewRobotTrackerService(cfg, generator, log)

    // 指定ポートでリッスン
    address := fmt.Sprintf(":%s", cfg.Port)
    lis, err := net.Listen("tcp", address)
    if err != nil {
        log.Error("ポートをリッスンできません: %v", err)
        os.Exit(1)
    }

    // gRPCサーバーを作成
    grpcServer := grpc.NewServer()

    // サービスを登録
    proto.RegisterRobotTrackerServer(grpcServer, trackerService)

    // 優雅なシャットダウンを処理
    go func() {
        c := make(chan os.Signal, 1)
        signal.Notify(c, os.Interrupt, syscall.SIGTERM)
        <-c
        log.Info("終了シグナルを受信、サービスをシャットダウン中...")
        grpcServer.GracefulStop()
    }()

    // サーバーを起動
    log.Info("robot-tracker サービスが %s で起動しました", address)
    if err := grpcServer.Serve(lis); err != nil {
        log.Error("サーバーエラー: %v", err)
        os.Exit(1)
    }
}